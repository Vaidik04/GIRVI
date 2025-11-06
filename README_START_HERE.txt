================================================================================
                    GIRVI MANAGEMENT SYSTEM - START HERE
================================================================================

GETTING SERVER ERROR? Follow these steps:

STEP 1: Stop the server (Press Ctrl+C)

STEP 2: Delete old database
    del instance\girvi.db

STEP 3: Start server
    python app.py

STEP 4: Login
    - Open: http://localhost:5000
    - Username: admin
    - Password: admin123

STEP 5: Complete shop profile (first time only)

STEP 6: Start using!
    - Add customers
    - Create loans
    - Everything will work now!

================================================================================
                            EVEN EASIER (Windows)
================================================================================

Just double-click one of these:

    EMERGENCY_FIX.bat      <-- Use this to fix server errors
    START_FRESH.bat        <-- Use this for clean start with backup

================================================================================
                               WHAT CHANGED?
================================================================================

We added USER DATA ISOLATION:
- Each user now has separate customers and loans
- Old database needs to be recreated with new structure
- This is a one-time fix

================================================================================
                              HELPFUL FILES
================================================================================

SERVER_ERROR_FIX.md        - Detailed fix for server errors
TROUBLESHOOTING.md         - Full troubleshooting guide
FIX_CUSTOMER_ERROR.md      - Fix customer saving errors
QUICK_START_GUIDE.md       - How to use the system

================================================================================
                           QUICK HELP REFERENCE
================================================================================

Problem: Server won't start
Fix: del instance\girvi.db && python app.py

Problem: Can't save customer
Fix: del instance\girvi.db && python app.py

Problem: Internal server error
Fix: del instance\girvi.db && python app.py

Problem: Database error
Fix: del instance\girvi.db && python app.py

Yes, the fix is the same! Just recreate the database.

================================================================================
                              SUPPORT
================================================================================

See TROUBLESHOOTING.md for detailed help.

================================================================================
