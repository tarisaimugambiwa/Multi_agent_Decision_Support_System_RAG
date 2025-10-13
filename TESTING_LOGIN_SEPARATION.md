# Quick Testing Guide - App vs Admin Login

## ✅ Test 1: App Login (Main Login)

### Step 1: Open Main App
1. Open browser
2. Go to: `http://127.0.0.1:8001/`
3. **Expected:** Home page loads

### Step 2: Click Login Button
1. Click "Login" button in navbar (top right)
2. **Expected:** Redirected to `/accounts/login/`
3. **Expected:** See **PURPLE GRADIENT** background
4. **Expected:** See **TWO COLUMNS**: Form (left) + Demo Credentials (right)
5. **Expected:** See **NO "Login As:" cards**

### Step 3: Test Nurse Login
1. Click the **PINK credential box** (Nurse Account)
2. **Expected:** Form auto-fills:
   - Username: `nurse`
   - Password: `nurse123`
3. **Expected:** Green border flash on fields (1 second)
4. Click "Sign In" button
5. **Expected:** Redirected to `/nurse-dashboard/`
6. **Expected:** See "Welcome Nurse Sarah Johnson"
7. **Expected:** Sidebar shows **5 menu items** only

### Step 4: Logout and Test Doctor
1. Click user dropdown (top right)
2. Click "Logout"
3. **Expected:** Back to login page
4. Click the **GREEN credential box** (Doctor Account)
5. **Expected:** Form auto-fills:
   - Username: `doctor`
   - Password: `doctor123`
6. Click "Sign In"
7. **Expected:** Redirected to `/doctor-dashboard/`
8. **Expected:** See "Welcome Dr. James Wilson"
9. **Expected:** Sidebar shows **4 menu items** + review

---

## ✅ Test 2: Admin Separation

### Step 1: Check System Admin Link
1. **While logged in as nurse/doctor:**
2. Look at sidebar menu
3. **Expected:** **NO "System Admin" link** visible
4. Look at user dropdown
5. **Expected:** **NO "System Admin" option**

### Step 2: Try Direct Admin Access
1. Manually type in browser: `http://127.0.0.1:8001/system-admin/`
2. **Expected:** Django admin login page appears (plain blue/white)
3. Try logging in with nurse credentials:
   - Username: `nurse`
   - Password: `nurse123`
4. **Expected:** **LOGIN FAILS** (not a superuser)
5. **Result:** ✅ Nurse cannot access admin panel

### Step 3: Verify Old Admin URL is Gone
1. Type in browser: `http://127.0.0.1:8001/admin/`
2. **Expected:** **404 Page Not Found** error
3. **Result:** ✅ Old admin URL no longer works

---

## ✅ Test 3: Login Button Always Goes to App

### Test from Home Page
1. Go to: `http://127.0.0.1:8001/`
2. Logout if logged in
3. Click "Login" button in navbar
4. **Expected:** Goes to `/accounts/login/` (app login)
5. **Expected:** **NOT** `/system-admin/` (admin login)
6. **Expected:** See purple gradient design

---

## ✅ Test 4: Demo Credentials Display

### Visual Check
1. Go to login page: `http://127.0.0.1:8001/accounts/login/`
2. **Expected to See:**
   ```
   RIGHT SIDE (Demo Credentials):
   
   🔑 Demo Credentials
   Click on any credential box to auto-fill the login form
   
   ┌──────────────────────────────────┐
   │ 👩‍⚕️ Nurse Account               │
   │    Limited Access                │
   │                                  │
   │ Username: nurse                  │
   │ Password: nurse123               │
   │                                  │
   │ 🖱️ Click to fill                 │
   └──────────────────────────────────┘
   
   ┌──────────────────────────────────┐
   │ 👨‍⚕️ Doctor Account              │
   │    Full Access                   │
   │                                  │
   │ Username: doctor                 │
   │ Password: doctor123              │
   │                                  │
   │ 🖱️ Click to fill                 │
   └──────────────────────────────────┘
   
   ℹ️ These are demonstration accounts for testing purposes only
   ```

3. **Expected NOT to See:**
   - ❌ "Login As:" label
   - ❌ Nurse/Doctor radio buttons or cards
   - ❌ Role selection dropdown

---

## ✅ Test 5: Auto-Fill Functionality

### Test Click-to-Fill
1. On login page, **clear both fields** (username and password)
2. Click **Nurse credential box**
3. **Expected:** 
   - Username field fills with "nurse"
   - Password field fills with "nurse123"
   - Green border appears on both fields
   - Green border disappears after 1 second
   - Focus moves to "Sign In" button
4. Clear fields again
5. Click **Doctor credential box**
6. **Expected:**
   - Username field fills with "doctor"
   - Password field fills with "doctor123"
   - Same green border animation
7. **Result:** ✅ Click-to-fill works perfectly

---

## ✅ Test 6: Mobile Responsiveness

### Desktop (> 991px)
1. Use browser at full width
2. **Expected:** Two columns side by side
3. Form on left, credentials on right

### Mobile (< 991px)
1. Resize browser to mobile width (e.g., 375px)
2. Or use browser DevTools → Device toolbar
3. **Expected:** Single column layout
4. Form appears first (top)
5. Credentials appear below (bottom)

---

## 🐛 Troubleshooting

### If You See Old Design with Role Cards:

1. **Hard refresh:** `Ctrl + Shift + R` or `Ctrl + F5`
2. **Clear cache:** Browser settings → Clear browsing data
3. **Incognito mode:** Open new private/incognito window
4. **Restart server:**
   ```powershell
   # Press Ctrl+C in terminal
   python manage.py runserver 8001
   ```

### If Admin Link Still Shows `/admin/`:

1. Check `templates/base.html` line 280
2. Should be: `/system-admin/` NOT `/admin/`
3. Check `templates/registration/login.html` line 433
4. Should be: `/system-admin/` NOT `/admin/`

### If Login Button Goes to Admin:

1. Check `templates/base.html` line 288
2. Should be: `href="/accounts/login/"` NOT `href="/admin/"`

---

## 📊 Success Criteria

All tests pass when:

| Test | Expected Result | Status |
|------|----------------|--------|
| 1. App login loads | Purple gradient, demo credentials visible | ✅ |
| 2. No role cards | "Login As:" section removed | ✅ |
| 3. Click-to-fill works | Form auto-fills, green flash | ✅ |
| 4. Nurse login | Redirects to nurse dashboard | ✅ |
| 5. Doctor login | Redirects to doctor dashboard | ✅ |
| 6. Login button URL | Goes to `/accounts/login/` | ✅ |
| 7. Admin separated | Nurse can't access `/system-admin/` | ✅ |
| 8. Old admin URL | `/admin/` returns 404 | ✅ |
| 9. No admin links | Regular users don't see admin link | ✅ |
| 10. Mobile responsive | Single column on mobile | ✅ |

---

## 🎯 What Changed Summary

### URLs:
- ❌ Removed: `/admin/` (old admin URL)
- ✅ Added: `/system-admin/` (new admin URL)
- ✅ Main login: `/accounts/login/` (unchanged)

### Templates:
- ✅ Updated: `templates/registration/login.html` (new design)
- ✅ Updated: `templates/base.html` (login button, admin link)

### Access Control:
- ✅ Changed: `is_staff` → `is_superuser` for admin access
- ✅ Separated: App users can't access Django admin

### Visual Design:
- ✅ Removed: Role selection cards
- ✅ Added: Demo credential boxes with click-to-fill
- ✅ Enhanced: Purple gradient background with animation

---

**Test Date:** October 13, 2025
**System:** Medical AI Diagnosis System
**Status:** Ready for Testing ✅
