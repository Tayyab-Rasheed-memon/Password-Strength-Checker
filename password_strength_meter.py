import streamlit as st
import re
import random
import string
import requests
from hashlib import sha1

# Custom CSS with animations
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes expertShine {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .header-container {
        animation: fadeIn 1s ease-out;
        text-align: center;
        padding: 2rem 0;
        border-bottom: 3px solid #2c3e50;
        margin-bottom: 2rem;
    }
    
    .expert-title {
        font-size: 1.4rem;
        background: linear-gradient(90deg, #2c3e50, #3498db, #2c3e50);
        background-size: 200% auto;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        display: inline-block;
        animation: expertShine 3s linear infinite;
        margin-top: 1rem;
    }
    
    .signature {
        font-family: 'Brush Script MT', cursive;
        font-size: 2rem;
        color: #3498db;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 0.5rem;
    }
    
    .metric-box:hover {
        transform: scale(1.02);
        transition: transform 0.3s ease;
    }
    
    @keyframes passwordPop {
        0% { transform: scale(0.9); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .generated-password {
        animation: passwordPop 0.5s ease-out;
        font-family: 'Courier New', monospace;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .copy-button {
        background: #3498db;
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .copy-button:hover {
        background: #2980b9;
        transform: scale(1.05);
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .copy-button:active {
        animation: bounce 0.4s ease;
    }
</style>
""", unsafe_allow_html=True)

# Personal Header Section
st.markdown("""
<div class="header-container">
    <div class="signature">Ibrahim Tayyab</div>
    <div style="color: #7f8c8d; margin-bottom: 0.5rem;">@Tayyab.R</div>
    <div class="expert-title">Password Strength Checker</div>
</div>
""", unsafe_allow_html=True)

def check_breached_password(password):
    """Check password against Have I Been Pwned database"""
    sha1password = sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1password[:5], sha1password[5:]
    try:
        response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
        if response.status_code == 200:
            hashes = (line.split(':') for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    return int(count)
    except Exception:
        return None
    return 0

def password_strength_analysis(password):
    analysis = {
        'length': len(password),
        'uppercase': bool(re.search(r'[A-Z]', password)),
        'lowercase': bool(re.search(r'[a-z]', password)),
        'digit': bool(re.search(r'\d', password)),
        'special': bool(re.search(r'[!@#$%^&*]', password)),
        'repeating': bool(re.search(r'(.)\1{2,}', password)),
        'sequences': bool(re.search(r'(1234|abcd|qwerty|asdfgh|zxcvbn)', password.lower())),
        'common': password.lower() in [p.lower() for p in common_passwords],
        'breach_count': check_breached_password(password)
    }
    return analysis

def calculate_score(analysis):
    score = 0
    if analysis['length'] >= 12: score += 3
    elif analysis['length'] >= 8: score += 2
    if analysis['uppercase']: score += 1
    if analysis['lowercase']: score += 1
    if analysis['digit']: score += 1
    if analysis['special']: score += 2
    if analysis['repeating']: score -= 1
    if analysis['sequences']: score -= 2
    if analysis['common']: score = 0
    return max(score, 0)

def generate_advanced_password(length=16, include_special=True, include_numbers=True):
    chars = string.ascii_letters
    if include_numbers: chars += string.digits
    if include_special: chars += '!@#$%^&*'
    
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        analysis = password_strength_analysis(password)
        if (analysis['uppercase'] and analysis['lowercase'] and 
            (not include_numbers or analysis['digit']) and 
            (not include_special or analysis['special'])):
            return password

common_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome']

col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.markdown('### Security Assessment')
    password = st.text_input("Enter password for analysis:", type="password")
    
    if password:
        with st.spinner("Analyzing security..."):
            analysis = password_strength_analysis(password)
            score = calculate_score(analysis)
            
            st.markdown('#### Security Score')
            progress_value = min(score / 10, 1.0)
            progress_color = "#2ecc71" if score >= 7 else "#f1c40f" if score >=4 else "#e74c3c"
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 1.5rem; margin-bottom: 1rem;">{score}/10</div>
                <div class="stProgress">
                    <div class="st-em" style="width: {progress_value*100}%;
                        background-color: {progress_color}; height: 10px; border-radius: 5px;">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('#### Vulnerability Report')
            if analysis['breach_count']:
                st.error(f"🚨 Breached {analysis['breach_count']} times")
            if analysis['common']:
                st.error("🚨 Common password pattern")
            if analysis['sequences']:
                st.warning("⚠️ Predictable sequence found")
            if analysis['repeating']:
                st.warning("⚠️ Repeating characters")
                
            st.markdown('#### Recommendations')
            if score < 7:
                rec_cols = st.columns(2)
                with rec_cols[0]:
                    st.markdown("**Essentials**")
                    if analysis['length'] < 12:
                        st.write("📏 12+ characters")
                    if not analysis['uppercase'] or not analysis['lowercase']:
                        st.write("🔠 Mixed cases")
                    if not analysis['special']:
                        st.write("⚡ Special chars")
                with rec_cols[1]:
                    st.markdown("**Advanced**")
                    st.write("🔀 Avoid patterns")
                    st.write("🔄 Randomize")
                    st.write("🚫 No personal info")
            else:
                st.success("✅ Excellent security!")

with col2:
    st.markdown('### Password Generator')
    with st.expander("Options", expanded=True):
        pwd_length = st.slider("Length", 12, 32, 16)
        include_upper = st.checkbox("Uppercase", True)
        include_lower = st.checkbox("Lowercase", True)
        include_numbers = st.checkbox("Numbers", True)
        include_special = st.checkbox("Special Chars", True)
    
    if st.button("Generate Password", use_container_width=True):
        new_pwd = generate_advanced_password(
            pwd_length,
            include_special=include_special,
            include_numbers=include_numbers
        )
        
        # Copy to clipboard
        try:
            pyperclip.copy(new_pwd)
            copy_success = True
        except:
            copy_success = False
        
        # Display password and copy button
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
            <div class="generated-password">{new_pwd}</div>
            <button class="copy-button" onclick="navigator.clipboard.writeText('{new_pwd}')">Copy</button>
        </div>
        """, unsafe_allow_html=True)
        
        if copy_success:
            st.success("Copied to clipboard!")
        else:
            st.error("Please copy manually")
        st.balloons()

st.markdown("---")
with st.expander("Security Guidelines"):
    st.markdown("""
    **Enterprise Standards**
    - 12+ character minimum
    - Mix character types
    - No personal info
    - Regular rotation
    - Unique per service
    """)

st.markdown("---")
st.caption("🔐 Secured by Ibrahim Tayyab | Password Strength Checker | v1.3.0")


























































































































# import streamlit as st
# import re
# import random
# import string
# import requests
# from hashlib import sha1

# # Custom CSS with animations
# st.markdown("""
# <style>
#     @keyframes fadeIn {
#         from { opacity: 0; transform: translateY(-20px); }
#         to { opacity: 1; transform: translateY(0); }
#     }
    
#     @keyframes expertShine {
#         0% { background-position: -200% 0; }
#         100% { background-position: 200% 0; }
#     }
    
#     .header-container {
#         animation: fadeIn 1s ease-out;
#         text-align: center;
#         padding: 2rem 0;
#         border-bottom: 3px solid #2c3e50;
#         margin-bottom: 2rem;
#     }
    
#     .expert-title {
#         font-size: 1.4rem;
#         background: linear-gradient(90deg, #2c3e50, #3498db, #2c3e50);
#         background-size: 200% auto;
#         color: white;
#         padding: 0.5rem 1rem;
#         border-radius: 25px;
#         display: inline-block;
#         animation: expertShine 3s linear infinite;
#         margin-top: 1rem;
#     }
    
#     .signature {
#         font-family: 'Brush Script MT', cursive;
#         font-size: 2rem;
#         color: #3498db;
#         text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
#         margin-bottom: 0.5rem;
#     }
    
#     .metric-box:hover {
#         transform: scale(1.02);
#         transition: transform 0.3s ease;
#     }
    
#     @keyframes passwordPop {
#         0% { transform: scale(0.9); opacity: 0; }
#         100% { transform: scale(1); opacity: 1; }
#     }
    
#     .generated-password {
#         animation: passwordPop 0.5s ease-out;
#     }
# </style>
# """, unsafe_allow_html=True)

# # Personal Header Section
# st.markdown("""
# <div class="header-container">
#     <div class="signature">Ibrahim Tayyab</div>
#     <div style="color: #7f8c8d; margin-bottom: 0.5rem;">@Tayyab.R</div>
#     <div class="expert-title">Password Strength checker</div>
# </div>
# """, unsafe_allow_html=True)

# def check_breached_password(password):
#     """Check password against Have I Been Pwned database"""
#     sha1password = sha1(password.encode('utf-8')).hexdigest().upper()
#     prefix, suffix = sha1password[:5], sha1password[5:]
#     try:
#         response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
#         if response.status_code == 200:
#             hashes = (line.split(':') for line in response.text.splitlines())
#             for h, count in hashes:
#                 if h == suffix:
#                     return int(count)
#     except Exception:
#         return None
#     return 0

# def password_strength_analysis(password):
#     analysis = {
#         'length': len(password),
#         'uppercase': bool(re.search(r'[A-Z]', password)),
#         'lowercase': bool(re.search(r'[a-z]', password)),
#         'digit': bool(re.search(r'\d', password)),
#         'special': bool(re.search(r'[!@#$%^&*]', password)),
#         'repeating': bool(re.search(r'(.)\1{2,}', password)),
#         'sequences': bool(re.search(r'(1234|abcd|qwerty|asdfgh|zxcvbn)', password.lower())),
#         'common': password.lower() in [p.lower() for p in common_passwords],
#         'breach_count': check_breached_password(password)
#     }
#     return analysis

# def calculate_score(analysis):
#     score = 0
#     if analysis['length'] >= 12: score += 3
#     elif analysis['length'] >= 8: score += 2
#     if analysis['uppercase']: score += 1
#     if analysis['lowercase']: score += 1
#     if analysis['digit']: score += 1
#     if analysis['special']: score += 2
#     if analysis['repeating']: score -= 1
#     if analysis['sequences']: score -= 2
#     if analysis['common']: score = 0
#     return max(score, 0)

# def generate_advanced_password(length=16, include_special=True, include_numbers=True):
#     chars = string.ascii_letters
#     if include_numbers: chars += string.digits
#     if include_special: chars += '!@#$%^&*'
    
#     while True:
#         password = ''.join(random.choice(chars) for _ in range(length))
#         analysis = password_strength_analysis(password)
#         if (analysis['uppercase'] and analysis['lowercase'] and 
#             (not include_numbers or analysis['digit']) and 
#             (not include_special or analysis['special'])):
#             return password

# common_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome']

# col1, col2 = st.columns([2, 1], gap="large")

# with col1:
#     st.markdown('### Security Assessment')
#     password = st.text_input("Enter password for analysis:", type="password")
    
#     if password:
#         with st.spinner("Analyzing security..."):
#             analysis = password_strength_analysis(password)
#             score = calculate_score(analysis)
            
#             st.markdown('#### Security Score')
#             progress_value = min(score / 10, 1.0)
#             progress_color = "#2ecc71" if score >= 7 else "#f1c40f" if score >=4 else "#e74c3c"
#             st.markdown(f"""
#             <div class="metric-box">
#                 <div style="font-size: 1.5rem; margin-bottom: 1rem;">{score}/10</div>
#                 <div class="stProgress">
#                     <div class="st-em" style="width: {progress_value*100}%;
#                         background-color: {progress_color}; height: 10px; border-radius: 5px;">
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
            
#             st.markdown('#### Vulnerability Report')
#             if analysis['breach_count']:
#                 st.error(f"🚨 Breached {analysis['breach_count']} times")
#             if analysis['common']:
#                 st.error("🚨 Common password pattern")
#             if analysis['sequences']:
#                 st.warning("⚠️ Predictable sequence found")
#             if analysis['repeating']:
#                 st.warning("⚠️ Repeating characters")
                
#             st.markdown('#### Recommendations')
#             if score < 7:
#                 rec_cols = st.columns(2)
#                 with rec_cols[0]:
#                     st.markdown("**Essentials**")
#                     if analysis['length'] < 12:
#                         st.write("📏 12+ characters")
#                     if not analysis['uppercase'] or not analysis['lowercase']:
#                         st.write("🔠 Mixed cases")
#                     if not analysis['special']:
#                         st.write("⚡ Special chars")
#                 with rec_cols[1]:
#                     st.markdown("**Advanced**")
#                     st.write("🔀 Avoid patterns")
#                     st.write("🔄 Randomize")
#                     st.write("🚫 No personal info")
#             else:
#                 st.success("✅ Excellent security!")

# with col2:
#     st.markdown('### Password Generator')
#     with st.expander("Options", expanded=True):
#         pwd_length = st.slider("Length", 12, 32, 16)
#         include_upper = st.checkbox("Uppercase", True)
#         include_lower = st.checkbox("Lowercase", True)
#         include_numbers = st.checkbox("Numbers", True)
#         include_special = st.checkbox("Special Chars", True)
    
#     if st.button("Generate Password", use_container_width=True):
#         new_pwd = generate_advanced_password(
#             pwd_length,
#             include_special=include_special,
#             include_numbers=include_numbers
#         )
#         st.markdown(f'<div class="generated-password">{new_pwd}</div>', 
#                    unsafe_allow_html=True)
#         st.success("Copied to clipboard!")
#         st.balloons()

# st.markdown("---")
# with st.expander("Security Guidelines"):
#     st.markdown("""
#     **Enterprise Standards**
#     - 12+ character minimum
#     - Mix character types
#     - No personal info
#     - Regular rotation
#     - Unique per service
#     """)

# st.markdown("---")
# st.caption("🔐 Secured by Ibrahim Tayyab | Password Strength checker | v1.2.0")


















# import streamlit as st
# import re
# import random
# import string
# import requests
# from hashlib import sha1

# # Custom CSS for professional styling
# st.markdown("""
# <style>
#     .stApp {
#         max-width: 1200px;
#         padding: 2rem 3rem;
#     }
#     .header {
#         border-bottom: 2px solid #2c3e50;
#         padding-bottom: 1rem;
#         margin-bottom: 2rem;
#     }
#     .section-title {
#         color: #2c3e50;
#         font-weight: 600;
#         margin: 1.5rem 0;
#     }
#     .metric-box {
#         background-color: #f8f9fa;
#         border-radius: 10px;
#         padding: 1.5rem;
#         margin: 1rem 0;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#     }
#     .generated-password {
#         font-family: 'Courier New', monospace;
#         font-size: 1.2rem;
#         letter-spacing: 2px;
#         padding: 1rem;
#         background: #f8f9fa;
#         border-radius: 5px;
#         text-align: center;
#     }
# </style>
# """, unsafe_allow_html=True)

# def check_breached_password(password):
#     """Check password against Have I Been Pwned database"""
#     sha1password = sha1(password.encode('utf-8')).hexdigest().upper()
#     prefix, suffix = sha1password[:5], sha1password[5:]
#     try:
#         response = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
#         if response.status_code == 200:
#             hashes = (line.split(':') for line in response.text.splitlines())
#             for h, count in hashes:
#                 if h == suffix:
#                     return int(count)
#     except Exception:
#         return None
#     return 0

# def password_strength_analysis(password):
#     analysis = {
#         'length': len(password),
#         'uppercase': bool(re.search(r'[A-Z]', password)),
#         'lowercase': bool(re.search(r'[a-z]', password)),
#         'digit': bool(re.search(r'\d', password)),
#         'special': bool(re.search(r'[!@#$%^&*]', password)),
#         'repeating': bool(re.search(r'(.)\1{2,}', password)),
#         'sequences': bool(re.search(r'(1234|abcd|qwerty|asdfgh|zxcvbn)', password.lower())),
#         'common': password.lower() in [p.lower() for p in common_passwords],
#         'breach_count': check_breached_password(password)
#     }
#     return analysis

# def calculate_score(analysis):
#     score = 0
#     # Positive factors
#     if analysis['length'] >= 12: score += 3
#     elif analysis['length'] >= 8: score += 2
#     if analysis['uppercase']: score += 1
#     if analysis['lowercase']: score += 1
#     if analysis['digit']: score += 1
#     if analysis['special']: score += 2
    
#     # Negative factors
#     if analysis['repeating']: score -= 1
#     if analysis['sequences']: score -= 2
#     if analysis['common']: score = 0  # Zero score if common password
#     return max(score, 0)

# def generate_advanced_password(length=16, include_special=True, include_numbers=True):
#     chars = string.ascii_letters
#     if include_numbers: chars += string.digits
#     if include_special: chars += '!@#$%^&*'
    
#     while True:
#         password = ''.join(random.choice(chars) for _ in range(length))
#         analysis = password_strength_analysis(password)
#         if (analysis['uppercase'] and analysis['lowercase'] and 
#             (not include_numbers or analysis['digit']) and 
#             (not include_special or analysis['special'])):
#             return password

# # Common passwords list
# common_passwords = ['password', '123456', 'qwerty', 'admin', 'welcome']

# # Streamlit UI
# st.title("🔒 Enterprise Password Security Suite")
# st.markdown('<div class="header"></div>', unsafe_allow_html=True)

# col1, col2 = st.columns([2, 1], gap="large")

# with col1:
#     st.markdown('### Security Assessment')
#     password = st.text_input("Enter password for analysis:", type="password", 
#                            help="We never store or transmit your password")
    
#     if password:
#         with st.spinner("Analyzing password security..."):
#             analysis = password_strength_analysis(password)
#             score = calculate_score(analysis)
            
#             # Security metrics
#             st.markdown('#### Security Score')
#             progress_value = min(score / 10, 1.0)
#             progress_color = "#2ecc71" if score >= 7 else "#f1c40f" if score >=4 else "#e74c3c"
#             st.markdown(f"""
#             <div class="metric-box">
#                 <div style="font-size: 1.5rem; margin-bottom: 1rem;">{score}/10</div>
#                 <div class="stProgress">
#                     <div class="st-em" data-testid="progress-bar" style="width: {progress_value*100}%;
#                         background-color: {progress_color}; height: 10px; border-radius: 5px;">
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
            
#             # Detailed analysis
#             st.markdown('#### Vulnerability Report')
#             if analysis['breach_count']:
#                 st.error(f"🚨 This password has appeared in {analysis['breach_count']} data breaches")
#             if analysis['common']:
#                 st.error("🚨 Password matches common known patterns")
#             if analysis['sequences']:
#                 st.warning("⚠️ Contains predictable character sequences")
#             if analysis['repeating']:
#                 st.warning("⚠️ Repeating characters detected")
                
#             # Strength recommendations
#             st.markdown('#### Recommendations')
#             if score < 7:
#                 rec_cols = st.columns(2)
#                 with rec_cols[0]:
#                     st.markdown("**Essential Requirements**")
#                     if analysis['length'] < 12:
#                         st.write("📏 Increase length to 12+ characters")
#                     if not analysis['uppercase'] or not analysis['lowercase']:
#                         st.write("🔠 Use mixed case letters")
#                     if not analysis['special']:
#                         st.write("⚡ Add special characters")
#                 with rec_cols[1]:
#                     st.markdown("**Advanced Security**")
#                     st.write("🔀 Avoid dictionary words")
#                     st.write("🔄 Use random character patterns")
#                     st.write("🚫 Remove personal information")
#             else:
#                 st.success("✅ Excellent password security!")

# with col2:
#     st.markdown('### Password Generator')
#     with st.expander("Advanced Options", expanded=True):
#         pwd_length = st.slider("Length", 12, 32, 16)
#         include_upper = st.checkbox("Uppercase (A-Z)", True)
#         include_lower = st.checkbox("Lowercase (a-z)", True)
#         include_numbers = st.checkbox("Numbers (0-9)", True)
#         include_special = st.checkbox("Special Characters", True)
    
#     if st.button("Generate Secure Password", use_container_width=True):
#         new_pwd = generate_advanced_password(
#             pwd_length,
#             include_special=include_special,
#             include_numbers=include_numbers
#         )
#         st.markdown(f'<div class="generated-password">{new_pwd}</div>', 
#                    unsafe_allow_html=True)
#         st.success("Password generated! Click the text to copy.")
#         st.balloons()

# st.markdown("---")
# with st.expander("Password Security Guidelines"):
#     st.markdown("""
#     **Enterprise Password Policy**
#     - Minimum 12 characters (16+ recommended)
#     - Combination of 4 character types:
#       - Uppercase letters (A-Z)
#       - Lowercase letters (a-z)
#       - Numbers (0-9)
#       - Special symbols (!@#$%^&*)
#     - No dictionary words or personal information
#     - No repeating characters (aaa) or sequences (1234)
#     - Regular password rotation (90 days)
#     - Unique passwords for each system/service
#     """)

# # Footer
# st.markdown("---")
# st.caption("""
# 🔐 Powered by Advanced Security Algorithms | 
# 📄 Compliant with NIST SP 800-63B | 
# 🛡️ End-to-end secure processing
# """)

































# import streamlit as st
# import re
# import random
# import string

# def check_password_strength(password):
#     score = 0
#     feedback = []
#     common_passwords = [
#         'password', '123456', 'password123', 'qwerty', '12345678', 
#         '111111', 'abc123', 'admin', 'welcome', 'letmein'
#     ]

#     # Check common passwords
#     if password.lower() in common_passwords:
#         feedback.append(("❌ Password is too common and easily guessable", 'red'))
#         return 0, feedback

#     # Length check
#     if len(password) >= 12:
#         score += 2
#         feedback.append(("✅ 12+ characters", 'green'))
#     elif len(password) >= 8:
#         score += 1
#         feedback.append(("⚠️ 8-11 characters (12+ recommended)", 'orange'))
#     else:
#         feedback.append(("❌ Too short (min 8 characters)", 'red'))

#     # Character variety checks
#     checks = {
#         'uppercase': r'[A-Z]',
#         'lowercase': r'[a-z]',
#         'digit': r'\d',
#         'special': r'[!@#$%^&*]'
#     }

#     for name, pattern in checks.items():
#         if re.search(pattern, password):
#             score += 1
#             feedback.append((f"✅ Contains {name}", 'green'))
#         else:
#             feedback.append((f"❌ Missing {name}", 'red'))

#     # Deduct points for patterns
#     if re.search(r'(.)\1{2,}', password):  # Repeating characters
#         score -= 1
#         feedback.append(("⚠️ Repeating characters detected", 'orange'))
    
#     if re.search(r'(1234|abcd|qwerty)', password.lower()):  # Common sequences
#         score -= 1
#         feedback.append(("⚠️ Common sequence detected", 'orange'))

#     # Ensure score doesn't go negative
#     score = max(score, 0)
    
#     return score, feedback

# def generate_strong_password(length=12):
#     characters = string.ascii_letters + string.digits + '!@#$%^&*'
#     while True:
#         password = ''.join(random.choice(characters) for _ in range(length))
#         if (re.search(r'[A-Z]', password) and
#             re.search(r'[a-z]', password) and
#             re.search(r'\d', password) and
#             re.search(r'[!@#$%^&*]', password)):
#             return password

# # Streamlit UI
# st.title("🔐 Password Strength Meter")
# st.write("Check your password security and generate strong passwords")

# col1, col2 = st.columns(2)

# with col1:
#     st.header("Password Checker")
#     password = st.text_input("Enter password to check:", type="password")
    
#     if password:
#         score, feedback = check_password_strength(password)
        
#         # Display strength meter
#         st.subheader("Security Assessment:")
#         progress = min(score/8, 1.0)  # Max 8 points possible
#         st.progress(progress)
        
#         # Display colored feedback
#         for msg, color in feedback:
#             if color == 'red':
#                 st.error(msg)
#             elif color == 'orange':
#                 st.warning(msg)
#             else:
#                 st.success(msg)

# with col2:
#     st.header("Password Generator")
#     pwd_length = st.slider("Select password length", 8, 20, 12)
#     if st.button("Generate Strong Password"):
#         new_pwd = generate_strong_password(pwd_length)
#         st.success("Generated Strong Password:")
#         st.code(new_pwd)
#         st.balloons()

# st.markdown("---")
# st.markdown("**Password Requirements:**")
# st.write("- Minimum 8 characters (12+ recommended)")
# st.write("- Mix of uppercase and lowercase letters")
# st.write("- At least one number")
# st.write("- At least one special character (!@#$%^&*)")
# st.write("- No common words or patterns")










































































































































# import re
# import random
# import string

# def check_password_strength(password):
#     score = 0
#     common_passwords = [
#         'password', '123456', 'password123', 'qwerty', '12345678', '111111',
#         'abc123', 'password1', '123123', 'admin', 'welcome', 'letmein',
#         'monkey', 'sunshine', 'master', 'hello', 'freedom', 'whatever',
#         'qazwsx', 'trustno1', 'dragon', 'baseball', 'superman', 'passw0rd',
#         'Password', 'Password1', 'Password123', 'P@ssw0rd', 'P@ssword'
#     ]
    
#     # Check against common passwords
#     if password.lower() in (p.lower() for p in common_passwords):
#         print("❌ Password is too common and easily guessable. Choose a unique password.")
#         print("❌ Weak Password - Avoid using common passwords.")
#         return 0  # Return score 0
    
#     # Length Check
#     if len(password) >= 8:
#         score += 1
#     else:
#         print("❌ Password should be at least 8 characters long.")
    
#     # Upper & Lowercase Check
#     if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
#         score += 1
#     else:
#         print("❌ Include both uppercase and lowercase letters.")
    
#     # Digit Check
#     if re.search(r"\d", password):
#         score += 1
#     else:
#         print("❌ Add at least one number (0-9).")
    
#     # Special Character Check
#     if re.search(r"[!@#$%^&*]", password):
#         score += 1
#     else:
#         print("❌ Include at least one special character (!@#$%^&*).")
    
#     # Check for repeating characters (3 or more)
#     if re.search(r"(.)\1{2,}", password):
#         print("❌ Avoid repeating the same character multiple times in a row.")
#         score -= 1  # Deduct one point
    
#     # Check for common sequences
#     common_sequences = [
#         '1234', '2345', '3456', '4567', '5678', '6789', '7890',
#         'abcd', 'bcde', 'cdef', 'defg', 'efgh', 'fghi', 'ghij',
#         'hijk', 'ijkl', 'jklm', 'klmn', 'lmno', 'mnop', 'nopq',
#         'opqr', 'pqrs', 'qrst', 'rstu', 'stuv', 'tuvw', 'uvwx',
#         'vwxy', 'wxyz', 'qwerty', 'asdfgh', 'zxcvbn', 'poiuyt',
#         'lkjhg', 'mnbvc'
#     ]
#     sequence_found = False
#     lower_password = password.lower()
#     for seq in common_sequences:
#         if seq in lower_password:
#             print(f"❌ Avoid using common sequences like '{seq}'.")
#             sequence_found = True
#             break
#     if sequence_found:
#         score -= 1  # Deduct one point
    
#     # Ensure score doesn't go below 0
#     score = max(score, 0)
    
#     # Strength Rating
#     if score >= 4:
#         print("✅ Strong Password!")
#     elif score >= 3:
#         print("⚠️ Moderate Password - Consider adding more security features.")
#     else:
#         print("❌ Weak Password - Improve it using the suggestions above.")
    
#     return score

# def generate_strong_password(length=12):
#     if length < 8:
#         length = 8  # Ensure minimum length
#     # Ensure at least one of each required type
#     uppercase = random.choice(string.ascii_uppercase)
#     lowercase = random.choice(string.ascii_lowercase)
#     digit = random.choice(string.digits)
#     special = random.choice('!@#$%^&*')
#     # Remaining characters
#     remaining = length - 4
#     all_chars = string.ascii_letters + string.digits + '!@#$%^&*'
#     rest = ''.join(random.choice(all_chars) for _ in range(remaining))
#     # Combine and shuffle
#     combined = list(uppercase + lowercase + digit + special + rest)
#     random.shuffle(combined)
#     return ''.join(combined)

# # Main program
# if __name__ == "__main__":
#     password = input("Enter your password: ")
#     score = check_password_strength(password)
    
#     if score < 4:  # If password is not Strong
#         generate = input("Would you like to generate a strong password? (yes/no): ").strip().lower()
#         if generate == 'yes':
#             new_password = generate_strong_password()
#             print("\nGenerated Strong Password:", new_password)
#             print("Please save this password in a secure place.")