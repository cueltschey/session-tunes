#!python3
r""" sql2puml.py - Convert SQL Schema to PlantUml Diagram


Dependencies
    py -m pip install sqlglot

"""
import argparse
import pathlib
import sys
import sqlglot
import requests
import zlib
import base64
import string

# newrel: the !define syntax is deprecated, but when I tried to remove these would work.
puml_template = """@startuml
!define table(x) class x << (T,#FFAAAA) >>
!define primary_key(x) <color:red>◆</color> x
!define foreign_key(x) <color:blue>◇</color> x
!function VARCHAR($x) !return "VARCHAR_" + $x

left to right direction
hide methods
hide stereotypes
skinparam classFontColor red
skinparam classAttributeIconSize 0
skinparam defaultFontName Courier

{tables}

{connections}

@enduml
"""


class SqlTable:
    def __init__(self, statement):
        if not isinstance(statement, sqlglot.expressions.Create):
            raise ValueError("Statement must be a CREATE TABLE statement")
        self.statement = statement

        # Create(this=Schema(this=Table(this=Identifier(this=TuneToSet
        self.name = statement.this.this.this.this
        self.primary_key = None  # primary key column name
        self.fields = dict()  # column_name : type
        self.foreign_keys = dict()  # field : Table::field

        self._extract_table_info()

    def _extract_table_info(self):
        for column in self.statement.find_all(sqlglot.expressions.ColumnDef):
            # Extract column name and type
            column_name = column.this.name
            column_type = str(column.kind)  # Get the SQL type as a string
            self.fields[column_name] = column_type

            # Check if this column has a primary key constraint
            if any(isinstance(c.kind, sqlglot.expressions.PrimaryKeyColumnConstraint) for c in column.constraints):
                self.primary_key = column_name

        for fk in self.statement.find_all(sqlglot.expressions.ForeignKey):
            local_column = self._extract_indentifier_from_expressions(fk)
            schema = fk.find(sqlglot.expressions.Reference).find(sqlglot.expressions.Schema)
            reference_table = schema.this.this.this
            reference_column = self._extract_indentifier_from_expressions(schema)
            self.foreign_keys[local_column] = f"{reference_table}::{reference_column}"
            #print(f"{local_column=}, {reference_table=}, {reference_column=}")

    def _extract_indentifier_from_expressions(self, node):
        for expression in node.args['expressions']:
            if isinstance(expression, sqlglot.expressions.Identifier):
                return expression.this
        return None

    def __repr__(self):
        return f"SqlTable(statement={repr(self.statement)})"

    def __str__(self):
        return f"SqlTable(name={self.name}, primary_key={self.primary_key}, fields={self.fields}, foreign_keys={self.foreign_keys})"

    @classmethod
    def parse_sql_file(cls, sql_file_path):
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()

        statements = sqlglot.parse(sql_content)
        for statement in statements:
            # Filter out anything that is not CREATE TABLE
            if isinstance(statement, sqlglot.expressions.Create):
                yield cls(statement)

    template = "table({name}) {{\n{fields}\n}}"
    def to_puml(self):
        fields = list()
        if self.primary_key:
            fields.append(f"    primary_key({self.primary_key}): {self.fields[self.primary_key]}")
        for fk in self.foreign_keys:
            fields.append(f"    foreign_key({fk}): {self.fields[fk]}")
        for field in self.fields:
            if field == self.primary_key:
                continue
            if field in self.foreign_keys:
                continue
            fields.append(f"    {field}: {self.fields[field]}")
        return self.template.format(
            name=self.name,
            fields="\n".join(fields))

# lifted from https://github.com/dougn/python-plantuml/blob/master/plantuml.py
plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
base64_alphabet   = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
b64_to_plantuml = bytes.maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))
def deflate_and_encode(plantuml_text):
    """zlib compress the plantuml text and encode it for the plantuml server.
    """
    zlibbed_str = zlib.compress(plantuml_text.encode('utf-8'))
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')


def parse():
    current_script_path = pathlib.Path(__file__).resolve()
    current_script_dir = current_script_path.parent
    #print(f"{current_script_path=}, {current_script_dir=}")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sql_file",
        type=pathlib.Path,
        default=current_script_dir / "init.sql",
        help="Filepath to the file containing the SQL commands that implement the database schema")
    parser.add_argument(
        "--puml_file",
        type=pathlib.Path,
        default=current_script_dir / "schema.puml",
        help="Filepath to the PlantUml that will be written")
    parser.add_argument(
        "--svg_file",
        type=pathlib.Path,
        default=current_script_dir / "schema.svg",
        help="Filepath to the SVG file that will be written")
    return parser.parse_args()


def main():
    args = parse()
    print(args)

    sql_tables = list()
    for sql_table in SqlTable.parse_sql_file(args.sql_file):
        sql_tables.append(sql_table)
    connections = list()
    left_reference = set()
    for sql_table in sql_tables:
        for fk, reference in sql_table.foreign_keys.items():
            if reference in left_reference:
                connections.append(f"{reference} o-- {sql_table.name}::{fk}")
            else:
                connections.append(f"{sql_table.name}::{fk} --o {reference}")
        if sql_table.primary_key:
            left_reference.add(f"{sql_table.name}::{sql_table.primary_key}")

    # Write the puml
    with args.puml_file.open('w', encoding='utf-8') as f:
        f.write(
            puml_template.format(
                tables="\n".join([sql_table.to_puml() for sql_table in sql_tables]),
                connections="\n".join(connections)))

    # Create the svg
    with args.puml_file.open('r', encoding='utf-8') as f:
        puml = f.read()
    #url = f"http://www.plantuml.com/plantuml/png/{encode_puml(puml)}"
    url = f'http://www.plantuml.com/plantuml/svg/{deflate_and_encode(puml)}'
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        with args.svg_file.open('wb') as f:
            f.write(response.content)
        print(f"Database schema definition at {args.sql_file} has been translated to Plant UML format in {args.puml_file} and saved as SVG in {args.svg_file}.")
    else:
        print(f"Failed to retrieve SVG file. Status code: {response.status_code}")


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
