# Kiosk Setup Guide

## BEC CRM System - Kiosk Station Configuration

**Version:** 1.0
**Last Updated:** October 2025
**Audience:** System administrators and facility managers

---

## Table of Contents

1. [Overview](#overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Hardware Setup](#hardware-setup)
4. [Software Configuration](#software-configuration)
5. [Browser Configuration](#browser-configuration)
6. [Kiosk Mode Setup](#kiosk-mode-setup)
7. [Security and Lock-Down](#security-and-lock-down)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Overview

The kiosk station allows members to self-check-in using their phone number. This guide covers setting up a dedicated kiosk computer or tablet.

### Kiosk Features

- Phone number lookup
- Touch-screen friendly interface
- Large, easy-to-read text
- Simple, intuitive workflow
- Automatic return to home screen
- No access to other functions

### User Flow

1. Member approaches kiosk
2. Enters 10-digit phone number
3. Selects their name from results
4. Clicks "Check In"
5. Sees confirmation message
6. Screen automatically resets after 5 seconds

---

## Hardware Requirements

### Minimum Requirements

**Option 1: Dedicated Computer**
- **Processor:** Intel/AMD dual-core 2.0GHz+
- **RAM:** 4GB minimum
- **Storage:** 32GB minimum
- **Display:** 15" minimum, touchscreen recommended
- **Network:** Ethernet or WiFi
- **OS:** Windows 10/11, macOS, or Linux

**Option 2: Tablet**
- **Device:** iPad (7th gen+), Android tablet, or Windows Surface
- **Screen Size:** 10" minimum
- **RAM:** 3GB minimum
- **Network:** WiFi with reliable connection
- **Mount:** Secure tablet mount or stand

**Option 3: All-in-One Touchscreen**
- 21-24" touchscreen all-in-one PC
- Built-in mount
- Clean, professional appearance

### Recommended Specifications

- **Touchscreen:** Capacitive, multi-touch
- **Screen Size:** 15-24" for visibility
- **Network:** Wired Ethernet for reliability
- **Mounting:** Wall-mount or secure floor stand
- **Power:** UPS/battery backup recommended

### Accessories

- **Keyboard/Mouse:** For initial setup only (remove after configuration)
- **Cable Management:** Keep power/network cables secure
- **Cleaning Supplies:** Screen cleaner and microfiber cloths
- **Optional:** Protective screen cover

---

## Hardware Setup

### Physical Placement

**Considerations:**
- High-traffic area near entrance
- Easy to see and access
- Good lighting (avoid glare on screen)
- Near power outlet
- Network connectivity available
- Secure mounting (prevent theft)

**Bad Locations:**
- Blocking doorways or walkways
- Near windows with direct sunlight
- In reach of liquids/spills
- Unstable surfaces

### Mounting Options

**Wall Mount:**
```
Pros:
- Saves floor space
- Professional appearance
- More secure
- At comfortable standing height

Installation:
1. Locate studs in wall
2. Mount bracket at 42-48" height
3. Secure monitor/computer to bracket
4. Run cables through wall or use conduit
5. Test stability
```

**Floor Stand:**
```
Pros:
- Portable/moveable
- No wall damage
- Easy installation

Installation:
1. Assemble stand per manufacturer instructions
2. Mount display to stand
3. Ensure base is weighted/stable
4. Cable management to prevent tripping
5. Consider locking stand to floor (optional)
```

**Desk/Counter Mount:**
```
Pros:
- Simple setup
- Easy access for maintenance
- Good for existing furniture

Installation:
1. Place on stable surface
2. Use non-slip mat
3. Cable management
4. Consider security cable lock
```

### Network Connection

**Wired Ethernet (Recommended):**
1. Run Cat5e/Cat6 cable to NAS location
2. Connect to network switch
3. Test connectivity: `ping YOUR_NAS_IP`
4. More reliable than WiFi

**WiFi:**
1. Connect to facility WiFi network
2. Ensure strong signal at kiosk location
3. Use 5GHz if available for better speed
4. Set static DHCP reservation for kiosk device

### Power Management

1. **Connect to UPS** (uninterruptible power supply)
2. **Configure power settings:**
   - Never sleep/hibernate
   - Never turn off display
   - Restart on power loss
3. **Hide power cables** to prevent accidental disconnection

---

## Software Configuration

### Operating System Setup

#### Windows 10/11

1. **Create dedicated kiosk user:**
   ```
   Settings → Accounts → Family & other users → Add someone else to this PC
   Username: "KioskUser"
   No password (or simple PIN)
   Standard user (not administrator)
   ```

2. **Disable Windows features:**
   - Windows Update pop-ups (set to manual)
   - Notifications
   - Cortana
   - Windows Defender notifications
   - Auto-restart after updates

3. **Set kiosk to auto-login:**
   ```
   Press Win+R, type: netplwiz
   Uncheck "Users must enter a username and password"
   Select KioskUser
   Click OK
   ```

4. **Configure power settings:**
   ```
   Control Panel → Power Options → Choose a power plan
   High Performance
   Change plan settings:
   - Turn off display: Never
   - Put computer to sleep: Never
   ```

#### macOS

1. **Create dedicated kiosk user:**
   ```
   System Preferences → Users & Groups
   Click + to add user
   Account type: Standard
   Username: "kioskuser"
   Enable automatic login
   ```

2. **Disable features:**
   - Disable Siri
   - Disable notifications
   - Disable automatic updates

3. **Energy Saver settings:**
   ```
   System Preferences → Energy Saver
   Prevent computer from sleeping: On
   Prevent display from sleeping: On
   Start up automatically after power failure: On
   ```

#### Linux

1. **Create kiosk user:**
   ```bash
   sudo adduser kioskuser
   ```

2. **Auto-login:**
   - Configure in display manager settings
   - Or edit `/etc/lightdm/lightdm.conf`

3. **Disable sleep:**
   ```bash
   sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
   ```

---

## Browser Configuration

### Browser Choice

**Recommended: Google Chrome**
- Best kiosk mode support
- Stable and well-tested
- Good touchscreen support
- Easy to configure

**Alternative: Firefox**
- Good kiosk support
- Privacy-focused
- Touchscreen compatible

### Chrome Setup

1. **Install Chrome:**
   - Download from google.com/chrome
   - Install with default settings

2. **Create kiosk shortcut:**

**Windows:**
```
Create new shortcut on desktop with target:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk --kiosk-printing "http://YOUR_NAS_IP:5173/kiosk"

Additional flags (optional):
--disable-pinch
--overscroll-history-navigation=0
--disable-features=TranslateUI
--no-first-run
--noerrdialogs
--disable-infobars
```

**macOS:**
```bash
# Create script: start_kiosk.sh
#!/bin/bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --kiosk "http://YOUR_NAS_IP:5173/kiosk"

# Make executable
chmod +x start_kiosk.sh

# Add to Login Items in System Preferences
```

**Linux:**
```bash
#!/bin/bash
google-chrome --kiosk "http://YOUR_NAS_IP:5173/kiosk"
```

3. **Set shortcut to auto-start:**

**Windows:**
- Press Win+R, type: `shell:startup`
- Copy kiosk shortcut to this folder
- Kiosk will start automatically on login

**macOS:**
- System Preferences → Users & Groups → Login Items
- Add start_kiosk.sh script

**Linux:**
- Add to autostart applications
- Or add to ~/.config/autostart/

### Firefox Setup

1. **Install Firefox**

2. **Install kiosk extension:**
   - Search for "Kiosk Mode" in Firefox Add-ons
   - Or use R-kiosk extension

3. **Configure:**
   - Set homepage to `http://YOUR_NAS_IP:5173/kiosk`
   - Enable fullscreen on start
   - Disable toolbars and navigation

---

## Kiosk Mode Setup

### Testing Kiosk Mode

Before locking down, test the interface:

1. **Open kiosk URL:** `http://YOUR_NAS_IP:5173/kiosk`
2. **Verify display:**
   - Large, readable text
   - Touch targets are easily tappable
   - No navigation bars or menus visible
3. **Test workflow:**
   - Enter phone number
   - Select client
   - Check in successfully
   - Screen resets automatically

### Advanced Kiosk Configuration

#### Disable Context Menus

**Chrome flags:**
```
--disable-context-menu
```

**CSS (if you can customize the kiosk page):**
```css
body {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
```

#### Auto-Refresh on Error

**Add to Chrome flags:**
```
--kiosk-printing
--disable-features=TranslateUI
--disable-session-crashed-bubble
--disable-crash-reporter
```

#### Network Error Handling

If kiosk loses connection:
1. Browser should auto-retry
2. Or configure auto-refresh every 5 minutes
3. Or use extension like "Super Auto Refresh"

---

## Security and Lock-Down

### Physical Security

1. **Secure mounting:** Prevent theft
2. **Hide/remove keyboard:** After setup complete
3. **Disable USB ports:** BIOS setting or physical cover
4. **Cable locks:** If portable device
5. **Screen protector:** Prevent damage

### Software Lock-Down

#### Windows Kiosk Mode

**Option 1: Assigned Access (Windows 10 Pro/Enterprise)**
```
Settings → Accounts → Other users → Set up kiosk
Choose app: Google Chrome
```

**Option 2: Shell Launcher**
- Replace explorer.exe with Chrome
- User cannot exit to desktop

**Option 3: Group Policy**
- Disable Task Manager
- Disable Alt+Tab
- Disable Windows key
- Disable Ctrl+Alt+Del

#### macOS Lock-Down

**Option 1: Single App Mode**
```bash
# For iPad/iOS devices
Settings → Accessibility → Guided Access
Enable and configure restrictions
```

**Option 2: Parental Controls**
```
System Preferences → Parental Controls
Limit applications to Chrome only
```

#### Linux Lock-Down

```bash
# Use window manager with restrictions
# Or custom kiosk distribution like Porteus Kiosk
```

### Browser Lock-Down

**Disable keyboard shortcuts:**
```
Chrome flags:
--disable-popup-blocking
--disable-translate
--disable-infobars
--disable-suggestions-service
--disable-save-password-bubble
```

**Prevent navigation away:**
- No address bar in kiosk mode
- No bookmark bar
- No developer tools
- No extensions menu

### Network Security

1. **Firewall rules:** Only allow access to CRM system
2. **DNS filtering:** Block other websites
3. **VLAN:** Isolate kiosk network (advanced)

---

## Testing

### Pre-Deployment Testing

**Checklist:**
- [ ] Kiosk loads automatically on startup
- [ ] Display is clear and readable
- [ ] Touchscreen responds accurately
- [ ] Phone number input works
- [ ] Client lookup works
- [ ] Check-in completes successfully
- [ ] Success message displays
- [ ] Screen resets after 5 seconds
- [ ] No way to exit kiosk mode
- [ ] Network connection is stable
- [ ] Power loss recovery works (restart and auto-resume)

### User Acceptance Testing

1. **Test with real members:**
   - Different phone numbers
   - Names with similar spellings
   - New vs experienced users

2. **Observe and note:**
   - Any confusion points
   - Screen height comfortable?
   - Touch targets easy to hit?
   - Speed acceptable?

3. **Adjust as needed:**
   - Screen angle
   - Height adjustment
   - Brightness
   - Font size (if customizable)

### Stress Testing

**Simulate busy periods:**
1. Multiple check-ins in sequence
2. Run for several hours continuously
3. Test during peak hours
4. Monitor for slowdowns or freezes

---

## Troubleshooting

### Kiosk Won't Load

**Symptoms:** Blank screen or error page

**Solutions:**
1. Check network connection: `ping YOUR_NAS_IP`
2. Check CRM system is running
3. Try URL in regular browser
4. Check firewall settings
5. Restart kiosk computer

### Touchscreen Not Responding

**Solutions:**
1. Clean screen (power off first)
2. Recalibrate touchscreen
3. Check touchscreen drivers
4. Test with mouse (if available)
5. Restart computer

### Members Can Exit Kiosk

**Solutions:**
1. Enable true kiosk mode (see [Security and Lock-Down](#security-and-lock-down))
2. Remove physical keyboard
3. Disable keyboard shortcuts
4. Use kiosk software/extension
5. Enable Assigned Access (Windows)

### Slow Performance

**Solutions:**
1. Close other applications
2. Check network speed
3. Clear browser cache
4. Restart kiosk daily (scheduled)
5. Check CRM system performance

### Screen Goes to Sleep

**Solutions:**
1. Adjust power settings (see [Software Configuration](#software-configuration))
2. Disable screen saver
3. Use "caffeine" type utility
4. Check for Windows updates changing settings

### Auto-Login Stops Working

**Solutions:**
1. Re-enable auto-login (see [Software Configuration](#software-configuration))
2. Check for Windows updates
3. Verify kiosk user password hasn't expired
4. Check for Group Policy changes

---

## Maintenance

### Daily

- [ ] Verify kiosk is operational (quick check)
- [ ] Wipe down screen
- [ ] Check for paper/trash around kiosk

### Weekly

- [ ] Deep clean screen and housing
- [ ] Test full check-in workflow
- [ ] Check for software updates
- [ ] Verify auto-login still working
- [ ] Check cables are secure

### Monthly

- [ ] Restart kiosk computer
- [ ] Clear browser cache (if not auto-clearing)
- [ ] Check for OS updates
- [ ] Verify power-loss recovery
- [ ] Review check-in logs for issues

### As Needed

- [ ] Update kiosk URL if NAS IP changes
- [ ] Adjust brightness seasonally (lighting changes)
- [ ] Update browser if security patches released
- [ ] Replace damaged screen protector

---

## Advanced Configuration

### Multiple Kiosk Stations

If you have multiple kiosks:

1. **Assign station IDs:**
   ```
   Station 1: http://YOUR_NAS_IP:5173/kiosk?station=1
   Station 2: http://YOUR_NAS_IP:5173/kiosk?station=2
   ```

2. **Track which station was used** (if CRM supports)

3. **Separate network:** Use different VLANs for isolation

### Custom Branding

If you want to customize the kiosk:

1. Add facility logo
2. Change colors to match branding
3. Custom welcome message
4. Custom success message

**Note:** Requires modifying web application code

### Integration with Door Access

If you have electronic door locks:

1. CRM system records check-in
2. Trigger unlock signal
3. Member enters facility

**Note:** Requires custom integration development

### Analytics

Track kiosk usage:
- Peak usage times
- Average check-in time
- Error rates
- Most common issues

Available in Reports section of admin interface.

---

## Quick Reference

### Kiosk URL
```
http://YOUR_NAS_IP:5173/kiosk
```

### Chrome Kiosk Command (Windows)
```
"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk "http://YOUR_NAS_IP:5173/kiosk"
```

### Emergency Exit Kiosk Mode
- **Windows:** Ctrl+Alt+Del → Task Manager → End Task
- **macOS:** Cmd+Q (if not disabled)
- **Linux:** Alt+F4 or Ctrl+Alt+Backspace

### Restart Kiosk
1. Exit kiosk mode
2. Restart computer
3. Kiosk should auto-start

### Contact

- **Admin Interface:** `http://YOUR_NAS_IP:5173`
- **API Documentation:** `http://YOUR_NAS_IP:8000/docs`
- **Technical Support:** [Your contact info]

---

## Appendix: Sample Hardware Setups

### Budget Setup (~$300)
- Raspberry Pi 4 (4GB RAM)
- 15" USB touchscreen monitor
- Simple stand or wall mount
- Keyboard for setup (remove after)

### Mid-Range Setup (~$600)
- Refurbished Dell/HP all-in-one touchscreen PC
- Wall mount bracket
- UPS battery backup

### Premium Setup (~$1500)
- New 22" touchscreen all-in-one PC
- Professional wall mount with cable management
- UPS battery backup
- Warranty and support

### Tablet Setup (~$400)
- iPad (10th generation) or Android tablet
- Secure tablet stand or wall mount
- MDM (Mobile Device Management) for kiosk mode

---

**Your kiosk is now ready to use!**

Members can check in independently, reducing wait times and improving their experience.
