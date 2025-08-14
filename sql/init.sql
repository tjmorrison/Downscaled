-- Initialize the snowpack portal database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic indexes for performance
-- (The actual tables will be created by SQLAlchemy)
