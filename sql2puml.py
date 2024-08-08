#!python3
r""" sql2puml.py - Convert SQL Schema to PlantUml Diagram


Dependencies
    py -m pip install sqlglot

"""
import argparse
import pathlib
import sys
import requests
import sqlglot

temp_tables = """table(Session) {
    primary_key(session_id):  INTEGER
    foreign_key(location_id): INTEGER
    session_date:  DATE
    start_time:    TIMESTAMP
    end_time:      TIMESTAMP
    description:   TEXT
}

table(SetToSession) {
    foreign_key(session_id): INTEGER
    foreign_key(set_id):     INTEGER
    set_index:    INTEGER
}

table(Location) {
    primary_key(location_id): INTEGER
    description:   TEXT
    address:       VARCHAR_255
    url:           VARCHAR_255
}

table(SetTable) {
    primary_key(set_id):    INTEGER
    description: TEXT
}

table(TuneToSet) {
    foreign_key(tune_id): INTEGER
    foreign_key(set_id):  INTEGER
    tune_index:INTEGER
}

table(Tune) {
    primary_key(tune_id): INTEGER
    name:      VARCHAR_255
    abc_path:  VARCHAR_255
    key:       VARCHAR_255
}"""

temp_connections = """Session::location_id --o Location::location_id
Session::session_id o- SetToSession::session_id
SetToSession::set_id -o SetTable::set_id
SetTable::set_id o- TuneToSet::set_id
TuneToSet::tune_id --o Tune::tune_id"""

puml_template = """@startuml
!define table(x) class x << (T,#FFAAAA) >>
!define primary_key(x) <color:red>◆</color> x
!define foreign_key(x) <color:blue>◇</color> x

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


def parse():
    current_script_path = pathlib.Path(__file__).resolve()
    current_script_dir = current_script_path.parent
    print(f"{current_script_path=}, {current_script_dir=}")
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
    for sql_table in sql_tables:
        print(sql_table)
    return

    # Write the puml
    with args.puml_file.open('w', encoding='utf-8') as f:
        f.write(
            puml_template.format(
                tables=temp_tables,
                connections=temp_connections))

    # create the svg


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
