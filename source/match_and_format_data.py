import pandas as pd
from datetime import datetime

def match_and_format_data(part_a, part_b):
    # Convert dates to datetime and extract months
    a_dates = [pd.to_datetime(d) for d in part_a['date']]
    b_dates = [pd.to_datetime(d) for d in part_b['date']]
    a_months = [d.month for d in a_dates]
    b_months = [d.month for d in b_dates]
    
    m = len(part_a['date'])
    n = len(part_b['date'])
    
    # Initialize DP table
    dp = [[0]*(n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            a_idx = i-1
            b_idx = j-1
            if (part_a['numbers'][a_idx] == part_b['numbers'][b_idx] and
                a_months[a_idx] == b_months[b_idx] and  # Match by month instead of year
                a_dates[a_idx] >= b_dates[b_idx]):
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Backtrack to find matched pairs
    i, j = m, n
    matched_pairs = []
    while i > 0 and j > 0:
        a_idx = i-1
        b_idx = j-1
        if (part_a['numbers'][a_idx] == part_b['numbers'][b_idx] and
            a_months[a_idx] == b_months[b_idx] and  # Match by month instead of year
            a_dates[a_idx] >= b_dates[b_idx] and
            dp[i][j] == dp[i-1][j-1] + 1):
            matched_pairs.append((a_idx, b_idx))
            i -= 1
            j -= 1
        else:
            if dp[i-1][j] > dp[i][j-1]:
                i -= 1
            else:
                j -= 1
    matched_pairs.reverse()
    
    # Sort matched pairs by part_a's date
    sorted_matched_pairs = sorted(matched_pairs, key=lambda x: a_dates[x[0]])
    
    # Prepare result with matched pairs
    result = []
    for pair in sorted_matched_pairs:
        a_idx, b_idx = pair
        a_date = part_a['date'][a_idx]
        a_num = part_a['numbers'][a_idx]
        b_date = part_b['date'][b_idx]
        b_num = part_b['numbers'][b_idx]
        result.append((a_date, a_num, b_date, b_num))
    
    # Collect unmatched a indices
    matched_a_indices = {p[0] for p in matched_pairs}
    unmatched_a = [i for i in range(len(part_a['date'])) if i not in matched_a_indices]
    
    # Insert unmatched a into result
    for i in unmatched_a:
        a_date = part_a['date'][i]
        a_num = part_a['numbers'][i]
        a_dt = a_dates[i]
        inserted = False
        for idx in range(len(result)):
            existing_a_date = result[idx][0]
            if existing_a_date is None:
                continue
            existing_dt = pd.to_datetime(existing_a_date)
            if a_dt < existing_dt:
                result.insert(idx, (a_date, a_num, None, None))
                inserted = True
                break
        if not inserted:
            result.append((a_date, a_num, None, None))
    
    # Collect unmatched b indices
    matched_b_indices = {p[1] for p in matched_pairs}
    unmatched_b = [j for j in range(len(part_b['date'])) if j not in matched_b_indices]
    
    # Insert unmatched b into result
    for j in unmatched_b:
        b_date = part_b['date'][j]
        b_num = part_b['numbers'][j]
        b_dt = b_dates[j]
        inserted = False
        for idx in range(len(result)):
            existing_b_date = result[idx][2]
            if existing_b_date is None:
                continue
            existing_dt = pd.to_datetime(existing_b_date)
            if b_dt < existing_dt:
                result.insert(idx, (None, None, b_date, b_num))
                inserted = True
                break
        if not inserted:
            result.append((None, None, b_date, b_num))
    
    # Create DataFrame
    df = pd.DataFrame(result, columns=['part_a.date', 'part_a.numbers', 'part_b.date', 'part_b.numbers'])
    return df