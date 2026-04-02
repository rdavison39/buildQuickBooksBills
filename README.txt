QuickBooks Bill Processing Automation (AutoHotkey)

Overview

These AutoHotkey scripts automate the processing of vendor bills in
QuickBooks Desktop.

They allow you to: - Select a vendor manually - Select a starting bill
manually - Automatically process all remaining bills - Resume processing
safely if interrupted

Files

processVendor.ahk Purpose: Controls the overall workflow. Opens each
bill, calls processBill, and moves to the next bill.

processBill.ahk Purpose: Processes individual bills and line items.

Controls

F2 - Process all bills F3 - Process one bill ESC - Stop immediately

Workflow

Open Bill Process Bill Save Bill Return to list Move Down Repeat

Save Dialog Handling

Case 1 — No Changes Bill closes immediately

Case 2 — Changes Made Recording Transaction dialog appears Script
automatically presses Yes

Debug Logging

Debug file: QuickBooks_Debug.log

Requirements

-   AutoHotkey v1.x
-   QuickBooks Desktop
-   Windows

Usage

1.  Open QuickBooks
2.  Navigate to Vendor Bills
3.  Select vendor
4.  Select starting bill
5.  Press F2

Best Practices

1.  Test with F3
2.  Verify behavior
3.  Run F2
4.  Use ESC if needed

Troubleshooting

If script skips rows: Check QuickBooks_Debug.log

If script stops early: Check dialog detection

Summary

These scripts provide: - Controlled automation - Safe processing - Easy
recovery - Reliable QuickBooks handling
