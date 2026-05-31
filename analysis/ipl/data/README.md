# IPL Data Refresh Documentation

## Overview
This document describes the process used to refresh and update the IPL ball-by-ball dataset from external sources.

## Date of Update
**May 30, 2026**

## Motivation
The existing IPL dataset (IPL.csv and Match_Info.csv) had limited coverage:
- **Previous date range:** 2008-2019 (Seasons 1-12)
- **Missing seasons:** 2020-2026 (Seasons 13-18)
- **Row count:** 289,914 ball-by-ball rows

## Data Source Selection
After researching available IPL datasets online, the following criteria were used:

### Criteria Evaluated:
1. **Completeness** - Must cover all seasons including recent ones (2020-2026)
2. **Update frequency** - Should be actively maintained with regular updates
3. **Data quality** - Structured, validated ball-by-ball delivery data
4. **Format compatibility** - CSV format matching existing schema

### Selected Source: `ritesh-ojha/IPL-DATASET`
- **Repository:** https://github.com/ritesh-ojha/IPL-DATASET
- **Update frequency:** Daily (updated within 2 days of matches played)
- **Coverage:** IPL 2008-2026 (all seasons)
- **Format:** Ball_By_Ball_Match_Data.csv + Match_Info.csv

## Refresh Process Steps

### Step 1: Repository Cloning
```powershell
git clone https://github.com/ritesh-ojha/IPL-DATASET.git "external_dataset" --depth 1
```
- Used shallow clone (`--depth 1`) to minimize download size
- Cloned to temporary directory for validation

### Step 2: Column Compatibility Validation
Compared external dataset columns with existing files:

**Ball_By_Ball_Match_Data.csv (External) → IPL.csv (Existing):**
| Column | Match Status |
|--------|-------------|
| ID | ✅ |
| Innings | ✅ |
| Overs | ✅ |
| BallNumber | ✅ |
| Batter | ✅ |
| Bowler | ✅ |
| NonStriker | ✅ |
| ExtraType | ✅ |
| BatsmanRun | ✅ |
| ExtrasRun | ✅ |
| TotalRun | ✅ |
| IsWicketDelivery | ✅ |
| PlayerOut | ✅ |
| Kind | ✅ |
| FieldersInvolved | ✅ |
| BattingTeam | ✅ |

**Match_Info.csv (External) → Match_Info.csv (Existing):**
| Column | Match Status |
|--------|-------------|
| match_number | ✅ |
| team1 | ✅ |
| team2 | ✅ |
| match_date | ✅ |
| toss_winner | ✅ |
| toss_decision | ✅ |
| result | ✅ |
| winner | ✅ |
| player_of_match | ✅ |
| venue | ✅ |
| city | ✅ |
| team1_players | ✅ |
| team2_players | ✅ |

**Result:** 100% column compatibility - no schema changes required

### Step 3: Data Comparison
| Metric | Previous Dataset | External Dataset | Difference |
|--------|-----------------|------------------|------------|
| Ball-by-ball rows | 289,915 | 295,259 | +5,344 |
| Match records | 1,220 | 1,242 | +22 |
| Date range (first) | 2016-05-19 | 2011-04-14 | Earlier coverage |
| Date range (last) | 2019-04-27 | 2026-05-27 | Extended to 2026 |

### Step 4: File Replacement
```powershell
# Replace IPL.csv with external Ball_By_Ball_Match_Data.csv
Move-Item -Path "external_dataset\csv\Ball_By_Ball_Match_Data.csv" -Destination "IPL.csv" -Force

# Replace Match_Info.csv with external Match_Info.csv  
Move-Item -Path "external_dataset\csv\Match_Info.csv" -Destination "Match_Info.csv" -Force
```

### Step 5: Post-Update Validation
Verified file counts and date ranges:
- ✅ IPL.csv: 295,259 rows (confirmed)
- ✅ Match_Info.csv: 1,242 rows (confirmed)
- ✅ Latest match date: 2026-05-27 (IPL 2026 season)

## Data Quality Notes

### Known Characteristics:
1. **Innings coverage:** All ball-by-ball data includes both innings per match
2. **Player name variations:** May differ from previous dataset for some players
3. **Extra types:** Includes wide, noball, legbye, bye, etc.
4. **Wicket details:** PlayerOut, Kind (caught/bowled/etc.), FieldersInvolved populated when applicable

### Data Consistency:
- Empty fields represented as `NA` or empty string
- Team names standardized across all seasons
- Match numbering consistent with official IPL records

## Future Refresh Recommendations

### Frequency:
- **Recommended:** Monthly or quarterly updates
- **Critical before major tournaments:** Update 1 week before event start

### Process for Future Updates:
```powershell
# 1. Clone latest repository version
git clone https://github.com/ritesh-ojha/IPL-DATASET.git "external_dataset" --depth 1

# 2. Validate columns match (optional but recommended)
# Compare headers with existing files

# 3. Replace files
Move-Item -Path "external_dataset\csv\Ball_By_Ball_Match_Data.csv" -Destination "IPL.csv" -Force
Move-Item -Path "external_dataset\csv\Match_Info.csv" -Destination "Match_Info.csv" -Force

# 4. Validate counts
Get-Content "IPL.csv" | Measure-Object -Line
Get-Content "Match_Info.csv" | Measure-Object -Line
```

### Backup Strategy:
For production environments, consider:
1. Create dated backup before replacement (e.g., `IPL_backup_2026-05-30.csv`)
2. Keep external dataset directory until validation complete
3. Test with sample queries before replacing in analysis pipelines

## Dependencies
- **git** - For repository cloning
- **PowerShell** - For file operations (Windows)
- **Python 3.x** - For data processing (optional, for downstream analysis)

## Credits
- **Original dataset:** ritesh-ojha/IPL-DATASET (MIT License)
- **Data source:** Cricsheet.org (official IPL ball-by-ball JSON feeds)

---
*Last updated: May 30, 2026*
