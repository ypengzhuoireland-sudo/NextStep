BEGIN;

-- Dashboard and exercise development seed script.
-- This script assumes the existing authentication schema has already created the users table.

CREATE TABLE IF NOT EXISTS knowledge_components (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS exercises (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    kc_id VARCHAR(100) NOT NULL REFERENCES knowledge_components(id),
    difficulty VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'ready',
    description TEXT NOT NULL,
    starter_code TEXT NOT NULL,
    test_cases JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE TABLE IF NOT EXISTS student_mastery (
    student_id VARCHAR(50) NOT NULL REFERENCES users(student_id),
    kc_id VARCHAR(100) NOT NULL REFERENCES knowledge_components(id),
    mastery FLOAT NOT NULL DEFAULT 0.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, kc_id),
    CONSTRAINT student_mastery_range CHECK (mastery >= 0.0 AND mastery <= 1.0)
);

CREATE INDEX IF NOT EXISTS idx_exercises_kc_id ON exercises(kc_id);
CREATE INDEX IF NOT EXISTS idx_exercises_difficulty ON exercises(difficulty);
CREATE INDEX IF NOT EXISTS idx_student_mastery_student_id ON student_mastery(student_id);

INSERT INTO knowledge_components (id, name, description) VALUES
('python_basics', 'Python Basics', 'Input, output, variables and simple expressions'),
('types_comparison', 'Types and Comparison', 'Data types, conversion and comparison operators'),
('conditionals', 'Conditionals', 'if, elif, else and boolean conditions'),
('loops', 'Loops', 'for loops, while loops and range'),
('lists', 'Lists', 'List creation, indexing and traversal'),
('functions', 'Functions', 'Function definition, parameters and return values')
ON CONFLICT (id) DO UPDATE
SET name = EXCLUDED.name,
    description = EXCLUDED.description;

INSERT INTO exercises (
    id, title, kc_id, difficulty, status, description, starter_code, test_cases
) VALUES
(
    'ex-001',
    'Format a Greeting',
    'python_basics',
    'easy',
    'ready',
    'Read a name from input and print a greeting in the format: Hello, <name>!',
    'name = input()
# Write your code here
',
    '[
        {"input": "Alice", "expected_output": "Hello, Alice!"},
        {"input": "Sam", "expected_output": "Hello, Sam!"}
    ]'::jsonb
),
(
    'ex-002',
    'Compare Two Numbers',
    'types_comparison',
    'easy',
    'ready',
    'Read two integers and print the larger value. If they are equal, print either value.',
    'a = int(input())
b = int(input())
# Write your code here
',
    '[
        {"input": "3\n7", "expected_output": "7"},
        {"input": "10\n4", "expected_output": "10"}
    ]'::jsonb
),
(
    'ex-003',
    'Temperature Advice',
    'conditionals',
    'medium',
    'ready',
    'Read a temperature as an integer. Print Cold if it is below 10, Warm if it is 10 to 25, and Hot otherwise.',
    'temperature = int(input())
# Write your code here
',
    '[
        {"input": "5", "expected_output": "Cold"},
        {"input": "18", "expected_output": "Warm"},
        {"input": "31", "expected_output": "Hot"}
    ]'::jsonb
),
(
    'ex-004',
    'Sum Numbers with a Loop',
    'loops',
    'medium',
    'recommended',
    'Read an integer n and print the sum of all numbers from 1 to n inclusive.',
    'n = int(input())
total = 0
# Write your loop here
print(total)
',
    '[
        {"input": "5", "expected_output": "15"},
        {"input": "10", "expected_output": "55"}
    ]'::jsonb
),
(
    'ex-005',
    'Find the Largest List Item',
    'lists',
    'medium',
    'ready',
    'Read a line of space-separated integers and print the largest number in the list.',
    'numbers = [int(x) for x in input().split()]
# Write your code here
',
    '[
        {"input": "4 8 2 6", "expected_output": "8"},
        {"input": "-3 -9 -1", "expected_output": "-1"}
    ]'::jsonb
)
ON CONFLICT (id) DO UPDATE
SET title = EXCLUDED.title,
    kc_id = EXCLUDED.kc_id,
    difficulty = EXCLUDED.difficulty,
    status = EXCLUDED.status,
    description = EXCLUDED.description,
    starter_code = EXCLUDED.starter_code,
    test_cases = EXCLUDED.test_cases;

-- Seed dashboard mastery for the default development user only if that user exists.
INSERT INTO student_mastery (student_id, kc_id, mastery)
SELECT 's1', seed.kc_id, seed.mastery
FROM (
    VALUES
        ('python_basics', 0.72),
        ('types_comparison', 0.58),
        ('conditionals', 0.64),
        ('loops', 0.46),
        ('lists', 0.51),
        ('functions', 0.39)
) AS seed(kc_id, mastery)
WHERE EXISTS (
    SELECT 1 FROM users WHERE student_id = 's1'
)
ON CONFLICT (student_id, kc_id) DO UPDATE
SET mastery = EXCLUDED.mastery,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;
