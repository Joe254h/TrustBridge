# TrustBridge - Complete Platform Guide

## 🎯 Overview

TrustBridge is a professional financial trust platform designed for informal workers in Lagos (and beyond) to build credibility through verified transactions. This complete version includes:

✅ **Full Authentication System** - Secure login/signup with password strength validation
✅ **OCR Receipt Scanning** - Extract amounts from handwritten and printed receipts
✅ **Advanced Trust Score Algorithm** - Multi-factor credit scoring system
✅ **Database Integration** - User data persistence (simulated, ready for MongoDB/PostgreSQL)
✅ **PDF Report Generation** - Password-protected, verifiable reports
✅ **Free & Premium Tiers** - Subscription management ready
✅ **Profile Management** - User profiles with image upload capability
✅ **Help Center** - Complete documentation and support
✅ **Professional UI** - Non-AI looking, clean, modern interface

---

## 🚀 Quick Start

### Installation

```bash
# 1. Install dependencies
pip install -r requirements_full.txt

# 2. Install Tesseract OCR (for receipt scanning)
# On Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# On macOS:
brew install tesseract

# On Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# 3. Run the app
streamlit run trustbridge_app.py

# 4. Open browser at http://localhost:8501
```

---

## 📱 Key Features Explained

### 1. Authentication & Security

**Sign Up:**
- Email validation
- Password strength indicator (shows weak/moderate/strong/very strong)
- Requires: uppercase, lowercase, number, special character, 8+ chars
- Accepts all special characters: !@#$%^&*(),.?":{}|<>
- Terms of service agreement

**Sign In:**
- Secure password hashing (SHA-256)
- Session management
- Remember me functionality

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### 2. Receipt OCR & Amount Extraction

**Supported Formats:**
- JPG, JPEG, PNG, PDF
- Handwritten receipts ✓
- Machine-generated receipts ✓
- Photos from phone camera ✓

**How It Works:**
1. Upload receipt image
2. OCR extracts text automatically
3. Smart regex patterns detect amounts:
   - Finds "TOTAL", "AMOUNT", currency symbols
   - Handles different formats: $45.50, ₦1,250.00, 82.30 NGN
4. Amount auto-fills in form
5. Manual override available

**Example Text Patterns Detected:**
```
TOTAL: $45.50
Amount Due: ₦1,250.00
Grand Total .... $82.30
AMOUNT PAID: 120.00 NGN
```

### 3. Trust Score Calculation

**Formula (300-850 scale):**

```python
Base Score = 300

+ Verified Transactions × 5 points each
+ Total Transactions × 1 point each  
+ Active Days × 2 points each
+ Regular Income: +10 points
+ Positive Cash Flow (Income > Expenses): +15 points
+ 30+ Day Streak: +20 points

Maximum Score = 850
```

**Score Tiers:**
- 750-850: Excellent (LEVEL 5) - All opportunities unlocked
- 650-749: Good (LEVEL 4) - Most opportunities
- 500-649: Building (LEVEL 3) - Some opportunities  
- 400-499: Fair (LEVEL 2) - Building trust
- 300-399: Starting (LEVEL 1) - New user

**Examples:**
- New user: 300 points
- 10 verified transactions: 300 + (10 × 5) + (10 × 1) = 360 points
- +15 active days: 360 + (15 × 2) = 390 points
- With regular income: 390 + 10 = 400 points
- Income > Expenses: 400 + 15 = 415 points

### 4. Database Structure

**Users Collection:**
```javascript
{
  email: "user@example.com",
  name: "John Doe",
  password: "hashed_password",
  plan: "free" | "premium",
  created_at: "2024-01-15T10:30:00",
  trust_score: 742,
  consistency_days: 45,
  profile_image: "base64_encoded_image"
}
```

**Transactions Collection:**
```javascript
{
  user_email: "user@example.com",
  date: "2024-01-15T10:30:00",
  type: "Income" | "Expense",
  amount: 450.00,
  category: "Freelance Pay",
  description: "Client project payment",
  verified: true,
  extracted_text: "Receipt text from OCR",
  created_at: "2024-01-15T10:30:00"
}
```

### 5. PDF Report Generation

**Report Types:**
1. Full Financial Summary
2. Income Verification Only
3. Trust Score Certificate
4. Transaction History

**Features:**
- Professional TrustBridge letterhead
- Trust score and tier display
- Transaction breakdown by category
- Income vs Expense charts
- Verification stamps
- QR code for online validation
- **Password protection** (code sent to email)

**Password Format:**
`TB-YYYYMMDD-XXXX`
Example: `TB-20240115-8B2F`

### 6. Free vs Premium

**Free Plan:**
- ✅ Unlimited transaction recording
- ✅ Basic trust score calculation
- ✅ 5 PDF reports per month
- ✅ Standard opportunities access
- ✅ Basic support (24-48 hours)

**Premium Plan ($9.99/month):**
- ⭐ Everything in Free
- ⭐ Advanced analytics dashboard
- ⭐ Unlimited encrypted PDF reports
- ⭐ Priority support (2-4 hours)
- ⭐ Custom transaction categories
- ⭐ Enhanced image verification
- ⭐ API access (coming soon)
- ⭐ Early access to new features

---

## 🎨 UI/UX Design Principles

**Non-AI Generated Look:**
- Clean, professional design
- Consistent spacing and alignment
- Real-world color palette (blues, greens, not purple/pink)
- Proper typography hierarchy
- No Comic Sans or playful fonts
- Professional icons (not emoji overload)
- Subtle shadows and borders
- Responsive grid layouts

**Color Scheme:**
- Primary: #2563EB (Professional Blue)
- Success: #10B981 (Green)
- Warning: #F59E0B (Orange)
- Danger: #EF4444 (Red)
- Gray Scale: #F8F9FA to #111827

---

## 📊 Dashboard Components

**Top Metrics Cards:**
1. Verified Monthly Income (with % change)
2. Consistency Streak (in weeks)
3. Verified Expenses (last updated time)
4. Report Readiness Status

**Trust Score Section:**
- Large circular progress indicator
- Score number (300-850)
- Current tier/level badge
- Progress bar to next tier
- Motivational message

**Core Actions:**
- Quick Income button (green)
- Quick Expense button (red)
- Net Monthly Flow display
- Verified records count

**Unlock Opportunities:**
- Apartment Rental Eligibility (progress bar)
- Micro-Loan Access (progress bar)  
- Job Verification Premium (progress bar)
- Apply buttons when unlocked

**Recent Activity Feed:**
- Last 5 transactions
- Icons for category
- Amount with +/- indicator
- Verification status (✓)
- Timestamp

---

## 🔐 Security Features

1. **Password Hashing:** SHA-256 encryption
2. **Session Management:** Secure user sessions
3. **Data Validation:** Input sanitization
4. **PDF Encryption:** Password-protected reports
5. **Email Verification:** Code-based access (production)
6. **HTTPS Ready:** SSL certificate support

---

## 🌐 Production Deployment

### Option 1: Streamlit Cloud (Free)

```bash
# 1. Push code to GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# 2. Go to share.streamlit.io
# 3. Connect GitHub repo
# 4. Deploy!
```

### Option 2: Heroku

```bash
# 1. Create Procfile
echo "web: streamlit run trustbridge_app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# 2. Create runtime.txt
echo "python-3.11.7" > runtime.txt

# 3. Deploy
heroku create trustbridge-app
git push heroku main
```

### Option 3: AWS/DigitalOcean

```bash
# 1. Install on Ubuntu server
sudo apt update
sudo apt install python3-pip tesseract-ocr
pip3 install -r requirements_full.txt

# 2. Run with PM2
pm2 start "streamlit run trustbridge_app.py --server.port=8501" --name trustbridge

# 3. Configure Nginx reverse proxy
# Point domain to server
```

### Database Integration (Production)

**MongoDB:**
```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["trustbridge"]
users = db["users"]
transactions = db["transactions"]
```

**PostgreSQL:**
```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="trustbridge",
    user="postgres",
    password="password"
)
```

---

## 🧪 Testing Accounts

You can create test accounts with these details:

**Test User 1:**
- Email: test@trustbridge.ng
- Name: Amina Johnson
- Password: Test@1234

**Test User 2:**
- Email: demo@trustbridge.ng
- Name: Sarah Jenning
- Password: Demo@5678

---

## 📸 Receipt Upload Examples

**What works:**
- Restaurant receipts
- Utility bills
- Grocery store receipts
- Handwritten invoices
- Bank statements
- Payment confirmations

**Tips for Best Results:**
- Good lighting
- Clear, focused image
- Entire receipt visible
- No blurry text
- Flat surface (not crumpled)

---

## 🆘 Troubleshooting

**Issue:** OCR not detecting amounts
**Solution:** Ensure Tesseract is installed, take clearer photos

**Issue:** Trust score not updating
**Solution:** Check that transactions are being saved with verified=True

**Issue:** Login not working
**Solution:** Clear browser cache, ensure cookies are enabled

**Issue:** PDF download fails
**Solution:** Check file permissions, ensure reportlab is installed

---

## 🚧 Roadmap (Future Features)

- [ ] Real-time SMS notifications (Africa's Talking API)
- [ ] WhatsApp integration for transaction updates
- [ ] Mobile app (React Native)
- [ ] Actual MongoDB/PostgreSQL integration
- [ ] Payment gateway (Paystack/Flutterwave)
- [ ] Loan application workflow
- [ ] Landlord portal
- [ ] Employer verification portal
- [ ] Multi-language support (English, Yoruba, Igbo, Hausa)
- [ ] USSD fallback for non-smartphone users
- [ ] Biometric verification
- [ ] Blockchain transaction proof

---

## 📧 Support

**Email:** support@trustbridge.ng
**WhatsApp:** +234 XXX XXX XXXX
**Website:** https://trustbridge.ng (coming soon)

---

## 📄 License

© 2024 @FinAfric. All rights reserved.

Built with ❤️ for informal workers in Lagos and beyond.

---

## 🙏 Credits

- **OCR:** Tesseract (Google)
- **Framework:** Streamlit
- **Icons:** Unicode/Emoji
- **Inspiration:** Financial inclusion in emerging markets
