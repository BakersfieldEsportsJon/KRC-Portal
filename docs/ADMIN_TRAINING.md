# Admin Training Guide

## BEC CRM System - Administrator User Guide

**Version:** 1.0
**Last Updated:** October 2025
**Audience:** System administrators and managers

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Clients](#managing-clients)
4. [Managing Memberships](#managing-memberships)
5. [User Management](#user-management)
6. [Check-In Management](#check-in-management)
7. [Reports and Analytics](#reports-and-analytics)
8. [System Settings](#system-settings)
9. [Best Practices](#best-practices)
10. [Common Tasks](#common-tasks)

---

## Getting Started

### First Login

1. Open your web browser
2. Navigate to: `http://YOUR_NAS_IP:5173` (or your configured domain)
3. Enter your admin credentials:
   - Email: `admin@bakersfieldesports.com`
   - Password: Your secure password

4. **First-time users:** You'll be prompted to change your temporary password
   - Choose a strong password (12+ characters)
   - Include uppercase, lowercase, numbers, and special characters
   - Click **Change Password**

### Interface Overview

The admin interface consists of:

- **Top Navigation Bar:**
  - Logo/Home
  - Navigation menu (Clients, Memberships, Check-ins, Reports, Admin)
  - User menu (Profile, Logout)

- **Main Content Area:**
  - Dynamic content based on current page
  - Tables, forms, and data displays

- **Action Buttons:**
  - Primary actions (Add, Edit, Delete)
  - Bulk actions (Export, Import)

### Navigation

- **Clients:** Manage customer information
- **Memberships:** Track and manage subscriptions
- **Check-ins:** View visit history
- **Reports:** Analytics and insights
- **Admin:** User management and system settings

---

## Dashboard Overview

### What You'll See

When you first login, the dashboard displays:

1. **Quick Stats:**
   - Total active members
   - Total clients
   - Check-ins today
   - Expiring memberships (next 30 days)

2. **Recent Activity:**
   - Latest check-ins
   - New client registrations
   - Recent membership changes

3. **Alerts and Notifications:**
   - Memberships expiring soon
   - System health status
   - Pending actions

4. **Quick Actions:**
   - Add new client
   - Check in a member
   - View reports

### Understanding the Numbers

- **Active Members:** Clients with current, non-expired memberships
- **Total Clients:** All clients in the system
- **Check-ins Today:** Number of visits recorded today
- **Expiring Soon:** Memberships ending within 30 days

---

## Managing Clients

### Adding a New Client

1. Click **Clients** in navigation
2. Click **Add Client** button
3. Fill in the form:

**Required Fields:**
- **First Name:** Client's first name
- **Last Name:** Client's last name
- **Phone:** 10-digit phone number (for kiosk check-in)

**Optional Fields:**
- **Email:** For email communications
- **Date of Birth:** For age verification or birthday messages
- **Notes:** Any additional information
- **Tags:** Categorize clients (VIP, Student, etc.)

4. Click **Save**

**Tips:**
- Phone numbers must be exactly 10 digits (no dashes or spaces)
- Email must be valid format
- Tags help organize and filter clients

### Searching for Clients

**Search Bar:**
- Located at top of Clients page
- Searches by name, phone, or email
- Updates results in real-time

**Filters:**
- **By Tag:** Filter clients with specific tags
- **By Membership Status:** Active, expired, or no membership
- **By Date Added:** Recently added clients

**Example Searches:**
- "John" - finds all Johns
- "555-1234" - finds phone numbers containing those digits
- "john@example.com" - finds exact email match

### Editing Client Information

1. Find client using search
2. Click on client name or **Edit** button
3. Update any fields
4. Click **Save Changes**

**Note:** Changing phone number affects kiosk check-in - inform the client

### Adding Contact Methods

Clients can have multiple contact methods (phone, email, SMS):

1. Open client details
2. Scroll to **Contact Methods** section
3. Click **Add Contact Method**
4. Select type (Phone, Email, SMS)
5. Enter contact information
6. Set preferences:
   - **Preferred:** Use this method first
   - **Consent:** Client agreed to be contacted
7. Click **Save**

### Managing Consents

Track client consent for communications:

1. Open client details
2. Scroll to **Consents** section
3. View consent status:
   - SMS marketing
   - Email marketing
   - Data processing

4. Update consent:
   - Toggle switches to update
   - System tracks when consent was given/revoked

**Important:** Always respect client consent preferences

### Tagging Clients

Tags help organize and filter clients:

**Common Tags:**
- VIP
- Student
- Staff
- Regular
- Tournament Player
- League Member

**Adding Tags:**
1. Open client details
2. Find **Tags** section
3. Start typing tag name
4. Select existing tag or create new
5. Click **Add**

**Using Tags:**
- Filter client list by tag
- Send targeted messages (if using Zapier integration)
- Generate reports by client segment

### Deleting Clients

**Use with caution** - this cannot be undone!

1. Open client details
2. Scroll to bottom
3. Click **Delete Client**
4. Confirm deletion

**What gets deleted:**
- Client information
- Associated memberships
- Check-in history
- Contact methods
- Consents

**Best Practice:** Instead of deleting, consider:
- Removing active memberships
- Adding "Inactive" tag
- Adding note explaining status

---

## Managing Memberships

### Adding a Membership

1. Navigate to **Clients** page
2. Find and open client
3. Scroll to **Membership** section
4. Click **Add Membership** or **Update Membership**
5. Fill in details:
   - **Start Date:** When membership begins
   - **End Date:** When membership expires
   - **Type:** Monthly, Annual, Day Pass, etc.
   - **Notes:** Any special conditions

6. Click **Save**

**Membership Status:**
- **Active:** Current date is between start and end dates
- **Expired:** Current date is after end date
- **Pending:** Current date is before start date

**Status is calculated automatically** - no need to update manually

### Renewing a Membership

1. Open client with expiring membership
2. View current membership details
3. Click **Renew**
4. System pre-fills form with:
   - Start Date: Day after current expiration
   - End Date: Calculated based on membership type
5. Adjust dates if needed
6. Click **Save**

**Tip:** You can renew before expiration - just set start date to current end date + 1 day

### Extending a Membership

To add time to existing membership:

1. Open client membership
2. Click **Edit**
3. Update **End Date** to new date
4. Add note explaining extension (e.g., "Comp for service issue")
5. Click **Save**

### Membership Types

You can track different membership types:

- **Monthly:** Typical 30-day membership
- **Annual:** 365-day membership
- **Day Pass:** Single day access
- **Week Pass:** 7-day access
- **Custom:** Any other duration

**Setting up Types:**
- Types are flexible text fields
- Use consistent naming for reporting
- Consider creating a standard list

### Viewing Expiring Memberships

1. Navigate to **Memberships** page
2. Click **Expiring Soon** filter
3. View all memberships expiring in next 30 days

**Proactive Management:**
- Review this list weekly
- Contact clients about renewal
- Prepare renewal reminders

### Membership Reports

Generate reports on memberships:

1. Navigate to **Reports**
2. Select **Membership Report**
3. Choose parameters:
   - Date range
   - Membership type
   - Status (active, expired, all)
4. Click **Generate**
5. View or export (CSV, PDF)

---

## User Management

### Overview

As an admin, you can:
- Create new staff accounts
- Reset staff passwords
- Deactivate accounts
- Manage roles and permissions

**User Roles:**
- **Admin:** Full access to all features
- **Staff:** Limited access (cannot manage users or settings)

### Creating a New Staff User

1. Navigate to **Admin** → **Users**
2. Click **Create User**
3. Fill in details:
   - **Email:** Must be unique
   - **Name:** User's full name
   - **Role:** Select "Staff" or "Admin"
4. Click **Create**

**What Happens:**
- System generates temporary password
- Password displayed once (copy it!)
- User must change password on first login

**Share credentials securely:**
- Tell user in person if possible
- Or use secure messaging
- Never send via regular email or text

### Resetting Staff Passwords

If staff member forgets password:

1. Navigate to **Admin** → **Users**
2. Find user in list
3. Click **Reset Password**
4. System generates new temporary password
5. Copy temporary password
6. Click **Confirm**
7. Share new password securely with staff
8. Staff must change on next login

**Security Note:** Staff cannot reset their own passwords - only admins can do this

### Deactivating a User

When staff leaves or no longer needs access:

1. Navigate to **Admin** → **Users**
2. Find user in list
3. Click **Deactivate** or **Delete**
4. Confirm action

**Deactivate vs Delete:**
- **Deactivate:** Keeps user record, prevents login
- **Delete:** Removes user completely

**Best Practice:** Deactivate instead of delete for audit trail

### Viewing User Activity

Track who did what:

1. Navigate to **Admin** → **Audit Log**
2. View activity history:
   - User who performed action
   - Action type (created, updated, deleted)
   - Timestamp
   - Details of change

3. Filter by:
   - User
   - Date range
   - Action type

**Use Cases:**
- Investigate data changes
- Track staff performance
- Compliance and auditing

---

## Check-In Management

### Viewing Check-Ins

1. Navigate to **Check-ins**
2. View list of all check-ins:
   - Client name
   - Check-in time
   - Method (phone, code, manual)
   - Station (if using multiple kiosks)

### Filtering Check-Ins

**By Date:**
- Today
- This Week
- This Month
- Custom date range

**By Client:**
- Search for specific client
- View their check-in history

**By Method:**
- Phone lookup
- Code lookup
- Manual check-in

### Manual Check-In

If kiosk is unavailable or client has issues:

1. Navigate to **Check-ins**
2. Click **Manual Check-In**
3. Search for client
4. Select client
5. Click **Check In**

**Use Cases:**
- Kiosk is down
- Client forgot phone
- Staff-assisted check-in
- Special circumstances

### Check-In Reports

1. Navigate to **Reports** → **Check-In Report**
2. Select date range
3. View metrics:
   - Total check-ins
   - Unique clients
   - Peak hours
   - Average visits per client

4. Export data for further analysis

**Insights:**
- Busiest days/times
- Most active members
- Client retention
- Traffic patterns

---

## Reports and Analytics

### Available Reports

1. **Membership Report:**
   - Active memberships
   - Expiring memberships
   - Revenue projections
   - Membership types breakdown

2. **Check-In Report:**
   - Daily/weekly/monthly traffic
   - Client visit frequency
   - Peak hours analysis
   - Retention metrics

3. **Client Report:**
   - Total clients
   - New clients by period
   - Client segmentation (tags)
   - Contact method preferences

4. **Financial Report** (if enabled):
   - Membership revenue
   - Renewal rates
   - Payment tracking

### Generating Reports

1. Navigate to **Reports**
2. Select report type
3. Configure parameters:
   - Date range
   - Filters (tags, membership types)
   - Grouping (by day, week, month)
4. Click **Generate**
5. View in browser or export

### Exporting Data

All reports can be exported:

**Export Formats:**
- **CSV:** For Excel/Google Sheets
- **PDF:** For printing/sharing
- **JSON:** For technical integrations

**Steps:**
1. Generate report
2. Click **Export**
3. Select format
4. Save file

### Using Data for Business Decisions

**Membership Renewals:**
- Track renewal rates
- Identify at-risk members
- Plan retention campaigns

**Facility Usage:**
- Identify peak hours
- Plan staffing accordingly
- Optimize resources

**Marketing:**
- Segment clients by activity
- Target inactive members
- Measure campaign effectiveness

---

## System Settings

### Accessing Settings

1. Navigate to **Admin** → **Settings**
2. View configuration options

### General Settings

- **Business Name:** Displayed in system
- **Timezone:** Affects dates and times
- **Default Membership Duration:** Default for new memberships

### Kiosk Settings

- **Enable Code Lookup:** Allow check-in by code
- **Require Membership:** Only allow members to check in
- **Custom Welcome Message:** Displayed on kiosk

### Messaging Settings (if enabled)

- **Zapier Integration:** Configure webhook URL
- **Default SMS Sender:** Phone number for SMS
- **Message Templates:** Customize automated messages

### Security Settings

- **Session Timeout:** How long users stay logged in
- **Password Policy:** Minimum password requirements
- **Two-Factor Authentication:** (if enabled)

### Backup Settings

- **Automatic Backups:** Enable/disable
- **Backup Frequency:** Daily, weekly
- **Retention Period:** How long to keep backups

**Important:** Ensure backups are enabled and working

---

## Best Practices

### Daily Tasks

**Morning Routine:**
- [ ] Check dashboard for alerts
- [ ] Review expiring memberships
- [ ] Verify system is running smoothly
- [ ] Check kiosk is operational

**Throughout Day:**
- [ ] Monitor check-ins
- [ ] Assist clients as needed
- [ ] Update client information promptly
- [ ] Process membership renewals

**Evening Routine:**
- [ ] Review day's check-ins
- [ ] Back up data (if not automated)
- [ ] Plan follow-ups for tomorrow
- [ ] Check for system updates

### Weekly Tasks

- [ ] Review expiring memberships report
- [ ] Contact members about renewals
- [ ] Generate check-in report
- [ ] Review staff activity (if applicable)
- [ ] Clean up inactive clients (if needed)
- [ ] Verify backups are completing

### Monthly Tasks

- [ ] Generate comprehensive reports
- [ ] Analyze trends and metrics
- [ ] Plan marketing campaigns
- [ ] Review and update client tags
- [ ] Audit user accounts
- [ ] Test backup restoration

### Data Entry Best Practices

**Be Consistent:**
- Use standard formats for phone numbers
- Use consistent tags
- Follow naming conventions

**Be Accurate:**
- Double-check phone numbers
- Verify email addresses
- Confirm dates carefully

**Be Complete:**
- Fill in all required fields
- Add notes for context
- Keep information current

### Security Best Practices

**Passwords:**
- Use strong, unique passwords
- Change passwords periodically
- Never share your admin password
- Use password manager

**Access Control:**
- Only give access to those who need it
- Use "Staff" role unless admin access truly needed
- Deactivate accounts promptly when staff leaves

**Data Protection:**
- Regular backups
- Verify backup integrity
- Keep system updated
- Monitor for suspicious activity

### Customer Service Best Practices

**Responsive:**
- Update client info when they request
- Process renewals promptly
- Respond to check-in issues quickly

**Professional:**
- Keep notes objective and professional
- Respect client privacy
- Handle data responsibly

**Proactive:**
- Reach out before memberships expire
- Identify and resolve issues early
- Suggest renewals and upgrades

---

## Common Tasks

### Task: New Member Sign-Up

1. **Collect Information:**
   - Get full name, phone, email
   - Explain membership options
   - Discuss consent for communications

2. **Create Client:**
   - Add new client in system
   - Enter all contact information
   - Add appropriate tags (e.g., "New Member")

3. **Add Membership:**
   - Set start date (today or future)
   - Set end date based on membership type
   - Add any notes about the membership

4. **Set Up Check-In:**
   - Verify phone number is correct
   - Show client how to use kiosk
   - Have them do a test check-in

5. **Follow Up:**
   - Welcome email/message (if using integrations)
   - Add to any relevant groups
   - Note any special requests

### Task: Processing a Renewal

1. **Find Client:**
   - Search by name or phone
   - Open client details

2. **Review Current Membership:**
   - Check expiration date
   - Review membership history
   - Check for any notes

3. **Add New Membership:**
   - Click "Renew"
   - Set start date (day after current expiration)
   - Set end date
   - Process payment (if applicable)

4. **Update Client Info:**
   - Verify contact information is current
   - Update if needed

5. **Confirmation:**
   - Thank client
   - Confirm new expiration date
   - Send receipt (if applicable)

### Task: Handling Expired Membership

**Client Arrives with Expired Membership:**

1. **Greet Client Politely:**
   - Check them in manually
   - Mention membership has expired

2. **Review Options:**
   - Offer renewal
   - Explain membership benefits
   - Discuss pricing

3. **Process Renewal:**
   - If they renew, add new membership
   - Set start date to today
   - Process payment

4. **If Not Renewing:**
   - Offer day pass (if available)
   - Explain consequences (may not be able to use kiosk)
   - Schedule follow-up

### Task: Troubleshooting Kiosk Issue

**Client Can't Check In:**

1. **Stay Calm and Professional:**
   - Assure client you'll help
   - Get details about the issue

2. **Verify Information:**
   - Confirm phone number
   - Check if client exists in system
   - Check membership status

3. **Common Fixes:**
   - Update phone number if incorrect
   - Manual check-in if kiosk is down
   - Renew membership if expired

4. **If Technical Issue:**
   - Use manual check-in
   - Note the issue
   - Contact tech support after assisting client

5. **Follow Up:**
   - Test kiosk after fix
   - Inform client issue is resolved

### Task: Monthly Reporting

1. **Generate Reports:**
   - Membership report for the month
   - Check-in report for the month
   - New client report

2. **Analyze Data:**
   - Calculate key metrics
   - Identify trends
   - Note any anomalies

3. **Create Summary:**
   - Total active members
   - New members added
   - Renewals processed
   - Average visits per member
   - Revenue (if tracking)

4. **Share Insights:**
   - Email to stakeholders
   - Present at team meeting
   - Plan actions based on data

5. **Archive:**
   - Save reports in organized folder
   - Note any action items
   - Set reminders for follow-up

---

## Keyboard Shortcuts

Speed up your workflow with shortcuts:

- **Ctrl + K** (or Cmd + K): Quick search
- **Ctrl + N** (or Cmd + N): New client/item
- **Ctrl + S** (or Cmd + S): Save changes
- **Ctrl + F** (or Cmd + F): Find on page
- **Esc**: Close modal/dialog

---

## Getting Help

### Built-In Help

- **API Documentation:** `http://YOUR_NAS_IP:8000/docs`
- **Tooltips:** Hover over icons for help text
- **Field Help:** Click ? icons for field explanations

### Documentation

- **Installation Guide:** `SYNOLOGY_INSTALLATION.md`
- **Troubleshooting:** `TROUBLESHOOTING.md`
- **Backup Guide:** `BACKUP_AND_MAINTENANCE.md`

### Support

If you encounter issues:

1. Check troubleshooting guide first
2. Review system logs
3. Note exact error message
4. Contact system administrator
5. Provide details:
   - What you were doing
   - What happened
   - What you expected
   - Screenshots if possible

---

## Training Checklist

**New Admin Training:**

- [ ] Successfully login and change password
- [ ] Navigate all major sections
- [ ] Add a new client
- [ ] Search for and edit a client
- [ ] Add a membership
- [ ] Process a renewal
- [ ] Perform manual check-in
- [ ] Generate a report
- [ ] Create a staff user
- [ ] Reset a staff password
- [ ] Export data
- [ ] Perform a backup
- [ ] Use kiosk interface

**After completing checklist, you're ready to manage the system independently!**

---

## Quick Reference

### Common Actions

| Action | Location | Steps |
|--------|----------|-------|
| Add Client | Clients → Add Client | Fill form, Save |
| Add Membership | Client Details → Add Membership | Set dates, Save |
| Manual Check-In | Check-ins → Manual Check-In | Search client, Check In |
| Generate Report | Reports → Select Type | Configure, Generate |
| Create User | Admin → Users → Create | Enter email/role, Create |
| Reset Password | Admin → Users → Reset Password | Confirm, Share new password |

### Contact Information

- **System Administrator:** [Your contact]
- **Technical Support:** [Support contact]
- **Emergency:** [Emergency contact]

---

**Congratulations! You're now trained on the BEC CRM System.**

Keep this guide handy for reference, and don't hesitate to explore the system to learn more.
