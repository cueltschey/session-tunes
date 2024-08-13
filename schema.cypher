// Create constraints
CREATE CONSTRAINT IF NOT EXISTS ON (l:Location) ASSERT l.location_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS ON (s:Session) ASSERT s.session_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS ON (st:SetTable) ASSERT st.set_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS ON (t:Tune) ASSERT t.tune_id IS UNIQUE;

// Create indexes
CREATE INDEX IF NOT EXISTS FOR (s:Session) ON (s.session_date);
CREATE INDEX IF NOT EXISTS FOR (t:Tune) ON (t.the_session_tune_id);

// Define node properties (similar to table columns)
CREATE (:Location {location_id: 0, description: '', address: '', url: ''});
CREATE (:Session {session_id: 0, session_date: date(), start_time: time(), end_time: time(), description: ''});
CREATE (:SetTable {set_id: 0, description: ''});
CREATE (:Tune {tune_id: 0, the_session_tune_id: 0, name: '', abc: '', tune_type: '', tune_meter: '', tune_mode: '', tune_url: ''});

// Create relationship types
CREATE ()-[:HELD_AT]->()
CREATE ()-[:INCLUDES_SET]->()
CREATE ()-[:CONTAINS_TUNE]->()
