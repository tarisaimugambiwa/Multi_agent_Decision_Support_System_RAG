# Quick Test Guide - Initial Load & Logout

## ✅ Test 1: Initial Load Without Login

### Steps:
1. **Open browser in incognito/private mode** (to ensure no cached session)
2. **Navigate to:** `http://127.0.0.1:8001/`
3. **Watch what happens**

### Expected Result:
- ✅ Browser automatically redirects to `/accounts/login/`
- ✅ You see the **purple gradient background**
- ✅ You see **two columns**: Login form (left) and Demo Credentials (right)
- ✅ You see clickable boxes for Nurse and Doctor credentials
- ✅ You do **NOT** see plain Django admin login page

### If You See This - ✅ SUCCESS:
```
Purple gradient background
┌─────────────────────────┐  ┌──────────────────┐
│ Medical AI System       │  │ 🔑 Demo          │
│ Sign in to continue     │  │ Credentials      │
│                         │  │                  │
│ [Username input]        │  │ 👩‍⚕️ Nurse       │
│ [Password input]        │  │ nurse/nurse123   │
│ ☐ Remember me           │  │                  │
│ [Sign In button]        │  │ 👨‍⚕️ Doctor      │
└─────────────────────────┘  │ doctor/doctor123 │
                             └──────────────────┘
```

### If You See This - ❌ PROBLEM:
```
Plain white/blue page
┌─────────────────────────┐
│ Django administration   │
│                         │
│ Username: [_______]     │
│ Password: [_______]     │
│ [ Log in ]              │
└─────────────────────────┘
```

---

## ✅ Test 2: Logout Redirect

### Steps:
1. **Login first** (if not already logged in)
   - Click the **pink Nurse box** on login page
   - Form auto-fills with `nurse` / `nurse123`
   - Click "Sign In"
   - You should now be on `/nurse-dashboard/`

2. **Look at top-right corner** of the page
   - You should see user dropdown with your name

3. **Click on your name/user dropdown**
   - A dropdown menu appears

4. **Click "Logout"** (red text at bottom of dropdown)

5. **Watch what happens**

### Expected Result:
- ✅ You are logged out (session cleared)
- ✅ Browser redirects to `/accounts/login/`
- ✅ You see the **purple gradient login page** again
- ✅ Demo credentials are visible
- ✅ You do **NOT** see Django admin login

### Visual Confirmation:
After clicking logout, you should see:
```
URL changes to: http://127.0.0.1:8001/accounts/login/
Page shows: Purple gradient with demo credentials
Navbar shows: No user info (logged out)
```

---

## ✅ Test 3: Login and Check Redirect

### Test Nurse Login:
1. On login page, click **pink "Nurse Account" box**
2. Form auto-fills: `nurse` / `nurse123`
3. Click "Sign In"

**Expected:**
- ✅ Redirected to `/nurse-dashboard/`
- ✅ See "Welcome Nurse Sarah Johnson" message
- ✅ Sidebar shows 5 menu items (limited access)

### Test Doctor Login:
1. Logout first
2. On login page, click **green "Doctor Account" box**
3. Form auto-fills: `doctor` / `doctor123`
4. Click "Sign In"

**Expected:**
- ✅ Redirected to `/doctor-dashboard/`
- ✅ See "Welcome Dr. James Wilson" message
- ✅ Sidebar shows 4 menu items + case review

---

## ✅ Test 4: Direct Dashboard Access (While Logged Out)

### Steps:
1. **Make sure you're logged out**
2. **Manually type in browser:** `http://127.0.0.1:8001/nurse-dashboard/`
3. **Press Enter**

### Expected Result:
- ✅ Redirected to `/accounts/login/?next=/nurse-dashboard/`
- ✅ See purple gradient login page
- ✅ After logging in, redirected back to nurse dashboard

### Repeat for Doctor:
1. Type: `http://127.0.0.1:8001/doctor-dashboard/`

**Expected:**
- ✅ Same behavior - redirected to login first
- ✅ After login, goes to doctor dashboard

---

## ✅ Test 5: System Admin Access (Separate System)

### Steps:
1. **Logout from app** (if logged in)
2. **Type in browser:** `http://127.0.0.1:8001/system-admin/`
3. **Press Enter**

### Expected Result:
- ✅ You see **plain Django admin login page** (blue/white)
- ✅ This is DIFFERENT from app login page
- ✅ Trying nurse/doctor credentials will FAIL here (not superuser)

### What This Proves:
- App login (`/accounts/login/`) and admin login (`/system-admin/`) are separate
- Nurse and doctor use app login only
- Only superusers can access system admin

---

## 🐛 Troubleshooting

### Problem: Still seeing Django admin login on initial load

**Solution:**
1. Clear browser cache: `Ctrl + Shift + Delete`
2. Close all browser windows
3. Open browser in incognito/private mode
4. Try again: `http://127.0.0.1:8001/`

### Problem: After logout, seeing dashboard instead of login

**Solution:**
1. Check `medical_ai/settings.py`:
   ```python
   LOGOUT_REDIRECT_URL = '/accounts/login/'  # Should be this
   ```
2. Restart Django server
3. Clear browser cache
4. Try logout again

### Problem: Getting 404 error on logout

**Solution:**
1. Check logout link in `templates/base.html`:
   ```html
   <a href="/accounts/logout/">Logout</a>  <!-- Should be this -->
   ```
2. Make sure URL is `/accounts/logout/` not `/logout/`

### Problem: Login page looks plain (no purple gradient)

**Solution:**
1. Hard refresh: `Ctrl + F5` or `Ctrl + Shift + R`
2. Check template file: `templates/registration/login.html`
3. Make sure it has purple gradient CSS
4. Clear browser cache

---

## 📊 Success Criteria

| Test | What to Check | Pass/Fail |
|------|--------------|-----------|
| Initial load | Opens to purple login page | ✅ |
| Not admin | Does NOT show Django admin | ✅ |
| Demo credentials | Visible and clickable | ✅ |
| Logout redirect | Goes to purple login page | ✅ |
| Not admin after logout | Does NOT show Django admin | ✅ |
| Nurse login | Redirects to nurse dashboard | ✅ |
| Doctor login | Redirects to doctor dashboard | ✅ |
| Protected URLs | Redirect to login if not auth | ✅ |
| Admin separate | `/system-admin/` is different | ✅ |

---

## 🎯 Quick Command Reference

### Restart Server:
```powershell
# Press Ctrl+C in terminal to stop
python manage.py runserver 8001
```

### Clear Browser Cache (Chrome/Edge):
```
Ctrl + Shift + Delete
→ Select "Cached images and files"
→ Click "Clear data"
```

### Open Incognito Mode:
```
Chrome/Edge: Ctrl + Shift + N
Firefox: Ctrl + Shift + P
```

### Check Server Logs:
Look in terminal where server is running for:
```
[13/Oct/2025 10:00:00] "GET / HTTP/1.1" 302 0
[13/Oct/2025 10:00:00] "GET /accounts/login/ HTTP/1.1" 200 26651
```
(302 = redirect, 200 = page loaded successfully)

---

## ✅ All Tests Should Pass!

If all tests pass:
- ✅ Initial load shows app login (purple gradient)
- ✅ Logout redirects to app login (purple gradient)
- ✅ No Django admin interference
- ✅ Demo credentials work perfectly
- ✅ Role-based redirects working

**System Status: ✅ READY FOR USE**

---

**Test Date:** October 13, 2025
**Tester:** _____________
**Result:** _____________
