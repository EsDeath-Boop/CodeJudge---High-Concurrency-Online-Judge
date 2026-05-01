-- CodeJudge seed: 8 competitive programming problems
-- Auto-runs on first DB boot via docker-entrypoint-initdb.d

-- Wait for tables to exist (created by FastAPI on startup)
-- This runs after postgres starts but the API may create tables later,
-- so we use a DO block with a retry.

DO $$
BEGIN
  -- Give FastAPI time to create tables on first run
  PERFORM pg_sleep(2);
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- PROBLEMS
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO problems (title, slug, description, difficulty, time_limit, memory_limit, sample_input, sample_output, is_active)
VALUES

-- 1. Two Sum
(
  'Two Sum',
  'two-sum',
  'Given an array of integers and a target sum, find two numbers that add up to the target.
Output their 1-based indices separated by a space. Guaranteed exactly one solution exists.

Input format:
- Line 1: N (number of elements)
- Line 2: N space-separated integers
- Line 3: target integer

Output: two 1-based indices i j (i < j) such that arr[i-1] + arr[j-1] = target',
  'easy', 2, 256,
  '4
2 7 11 15
9',
  '1 2',
  true
),

-- 2. Valid Parentheses
(
  'Valid Parentheses',
  'valid-parentheses',
  'Given a string containing only the characters (, ), {, }, [ and ], determine if the input string is valid.

A string is valid if:
- Every open bracket is closed by the same type of bracket.
- Open brackets are closed in the correct order.
- Every close bracket has a corresponding open bracket.

Input: a single string on one line
Output: YES if valid, NO otherwise',
  'easy', 2, 256,
  '({[]})
',
  'YES',
  true
),

-- 3. Longest Common Subsequence
(
  'Longest Common Subsequence',
  'longest-common-subsequence',
  'Given two strings, find the length of their longest common subsequence (LCS).

A subsequence is a sequence that appears in the same relative order but not necessarily contiguous.

Input format:
- Line 1: string A
- Line 2: string B

Output: length of LCS',
  'medium', 3, 256,
  'ABCBDAB
BDCAB',
  '4',
  true
),

-- 4. Maximum Subarray
(
  'Maximum Subarray',
  'maximum-subarray',
  'Given an integer array, find the contiguous subarray with the largest sum and return its sum.
Solve using Kadane''s algorithm in O(N).

Input format:
- Line 1: N (number of elements)
- Line 2: N space-separated integers (may include negatives)

Output: maximum subarray sum',
  'easy', 2, 256,
  '9
-2 1 -3 4 -1 2 1 -5 4',
  '6',
  true
),

-- 5. Number of Islands
(
  'Number of Islands',
  'number-of-islands',
  'Given a 2D binary grid of 1s (land) and 0s (water), count the number of islands.
An island is surrounded by water and formed by connecting adjacent land cells (4-directionally).

Input format:
- Line 1: R C (rows and columns)
- Next R lines: C space-separated values (0 or 1)

Output: number of islands',
  'medium', 3, 256,
  '4 5
1 1 0 0 0
1 1 0 0 0
0 0 1 0 0
0 0 0 1 1',
  '3',
  true
),

-- 6. Merge K Sorted Lists (simplified)
(
  'Merge Sorted Arrays',
  'merge-sorted-arrays',
  'Given K sorted arrays, merge them into one sorted array.

Input format:
- Line 1: K (number of arrays)
- Next K lines: each starts with N (size) followed by N sorted integers

Output: all elements merged and sorted on one line, space-separated',
  'medium', 3, 256,
  '3
3 1 4 7
4 2 5 6 8
2 0 9',
  '0 1 2 4 5 6 7 8 9',
  true
),

-- 7. Shortest Path (BFS)
(
  'Shortest Path in Grid',
  'shortest-path-grid',
  'Find the shortest path from the top-left to the bottom-right of a grid.
You can move up, down, left, right. Cells marked 1 are passable, 0 are walls.

Input format:
- Line 1: R C (rows and columns)
- Next R lines: C space-separated values (0 or 1)

Output: minimum steps to reach bottom-right, or -1 if no path exists.
(Start and end cells are always 1)',
  'medium', 3, 256,
  '4 4
1 0 0 0
1 1 0 1
0 1 0 0
0 1 1 1',
  '6',
  true
),

-- 8. Segment Tree Range Sum
(
  'Range Sum Query',
  'range-sum-query',
  'Given an array, answer Q range sum queries of the form [L, R] (1-indexed, inclusive).

Input format:
- Line 1: N (array size)
- Line 2: N space-separated integers
- Line 3: Q (number of queries)
- Next Q lines: L R

Output: Q lines, each with the sum of elements from index L to R (1-indexed)',
  'hard', 3, 256,
  '5
1 3 5 7 9
3
1 3
2 4
1 5',
  '9
15
25',
  true
)

ON CONFLICT (slug) DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- TEST CASES
-- ─────────────────────────────────────────────────────────────────────────────

-- Helper: get problem IDs by slug
DO $$
DECLARE
  pid_two_sum              INT;
  pid_parens               INT;
  pid_lcs                  INT;
  pid_max_sub              INT;
  pid_islands              INT;
  pid_merge                INT;
  pid_shortest             INT;
  pid_range                INT;
BEGIN

SELECT id INTO pid_two_sum   FROM problems WHERE slug='two-sum';
SELECT id INTO pid_parens    FROM problems WHERE slug='valid-parentheses';
SELECT id INTO pid_lcs       FROM problems WHERE slug='longest-common-subsequence';
SELECT id INTO pid_max_sub   FROM problems WHERE slug='maximum-subarray';
SELECT id INTO pid_islands   FROM problems WHERE slug='number-of-islands';
SELECT id INTO pid_merge     FROM problems WHERE slug='merge-sorted-arrays';
SELECT id INTO pid_shortest  FROM problems WHERE slug='shortest-path-grid';
SELECT id INTO pid_range     FROM problems WHERE slug='range-sum-query';

-- ── Two Sum ────────────────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_two_sum, '4
2 7 11 15
9', '1 2', true, 0),
(pid_two_sum, '3
3 2 4
6', '2 3', false, 1),
(pid_two_sum, '2
3 3
6', '1 2', false, 2),
(pid_two_sum, '6
1 5 3 7 2 8
10', '2 4', false, 3),
(pid_two_sum, '5
0 4 3 0 5
0', '1 4', false, 4)
ON CONFLICT DO NOTHING;

-- ── Valid Parentheses ──────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_parens, '({[]})', 'YES', true, 0),
(pid_parens, '()', 'YES', false, 1),
(pid_parens, '()[]{}'  , 'YES', false, 2),
(pid_parens, '(]', 'NO', false, 3),
(pid_parens, '([)]', 'NO', false, 4),
(pid_parens, '{[]}', 'YES', false, 5),
(pid_parens, '', 'YES', false, 6),
(pid_parens, '((((', 'NO', false, 7)
ON CONFLICT DO NOTHING;

-- ── LCS ───────────────────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_lcs, 'ABCBDAB
BDCAB', '4', true, 0),
(pid_lcs, 'AGGTAB
GXTXAYB', '4', false, 1),
(pid_lcs, 'ABC
ABC', '3', false, 2),
(pid_lcs, 'ABC
DEF', '0', false, 3),
(pid_lcs, 'ABCDEF
ACE', '3', false, 4),
(pid_lcs, 'A
A', '1', false, 5)
ON CONFLICT DO NOTHING;

-- ── Maximum Subarray ───────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_max_sub, '9
-2 1 -3 4 -1 2 1 -5 4', '6', true, 0),
(pid_max_sub, '1
1', '1', false, 1),
(pid_max_sub, '5
-1 -2 -3 -4 -5', '-1', false, 2),
(pid_max_sub, '4
1 2 3 4', '10', false, 3),
(pid_max_sub, '8
5 4 -1 7 8 -10 3 2', '23', false, 4),
(pid_max_sub, '3
-2 -1 -3', '-1', false, 5)
ON CONFLICT DO NOTHING;

-- ── Number of Islands ──────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_islands, '4 5
1 1 0 0 0
1 1 0 0 0
0 0 1 0 0
0 0 0 1 1', '3', true, 0),
(pid_islands, '4 5
1 1 1 1 0
1 1 0 1 0
1 1 0 0 0
0 0 0 0 0', '1', false, 1),
(pid_islands, '4 5
1 1 0 0 0
1 1 0 0 0
0 0 0 1 1
0 0 0 1 1', '2', false, 2),
(pid_islands, '1 1
1', '1', false, 3),
(pid_islands, '2 2
0 0
0 0', '0', false, 4),
(pid_islands, '3 3
1 0 1
0 1 0
1 0 1', '5', false, 5)
ON CONFLICT DO NOTHING;

-- ── Merge Sorted Arrays ────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_merge, '3
3 1 4 7
4 2 5 6 8
2 0 9', '0 1 2 4 5 6 7 8 9', true, 0),
(pid_merge, '2
3 1 3 5
3 2 4 6', '1 2 3 4 5 6', false, 1),
(pid_merge, '1
4 1 2 3 4', '1 2 3 4', false, 2),
(pid_merge, '3
2 1 4
2 2 3
2 5 6', '1 2 3 4 5 6', false, 3),
(pid_merge, '2
1 100
1 200', '100 200', false, 4)
ON CONFLICT DO NOTHING;

-- ── Shortest Path Grid ─────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_shortest, '4 4
1 0 0 0
1 1 0 1
0 1 0 0
0 1 1 1', '6', true, 0),
(pid_shortest, '2 2
1 1
1 1', '2', false, 1),
(pid_shortest, '2 2
1 0
0 1', '-1', false, 2),
(pid_shortest, '3 3
1 1 1
0 0 1
0 0 1', '4', false, 3),
(pid_shortest, '1 1
1', '0', false, 4),
(pid_shortest, '3 4
1 1 1 1
0 0 0 1
0 0 0 1', '5', false, 5)
ON CONFLICT DO NOTHING;

-- ── Range Sum Query ────────────────────────────────────────────────────────
INSERT INTO test_cases (problem_id, input_data, expected_output, is_sample, order_index) VALUES
(pid_range, '5
1 3 5 7 9
3
1 3
2 4
1 5', '9
15
25', true, 0),
(pid_range, '6
2 4 6 8 10 12
4
1 6
2 5
3 4
1 1', '42
28
14
2', false, 1),
(pid_range, '3
-1 2 -3
2
1 3
2 2', '-2
2', false, 2),
(pid_range, '1
42
1
1 1', '42', false, 3),
(pid_range, '4
1 2 3 4
3
1 4
2 3
4 4', '10
5
4', false, 4)
ON CONFLICT DO NOTHING;

END $$;
