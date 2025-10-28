# Recovery Key System Design - CCMD v1.2.0

**Status:** Design Mockup (Not Implemented)
**Target Release:** v1.2.0
**Security Level:** High

---

## Overview

Implement a **single-use backup code system** to allow users to recover access if they forget their master password. This follows industry best practices used by GitHub, Google, and other security-conscious platforms.

---

## Key Features

### 1. Single-Use Backup Codes
- **10 unique recovery codes** generated during setup
- Each code can only be used **once**
- Codes are **cryptographically random** (16 characters, alphanumeric)
- Format: `XXXX-XXXX-XXXX-XXXX` (easy to read and type)

### 2. Secure Storage
- Codes stored hashed with **bcrypt** (or PBKDF2 fallback)
- File location: `~/.ccmd/recovery_codes.key`
- Permissions: **0600** (owner-only access)
- Each code stored separately to allow individual deletion

### 3. Usage Flow
- User can use recovery code **instead of master password**
- After successful use, code is **immediately deleted**
- User is prompted to generate new codes when running low (< 3 remaining)

---

## User Experience Mockup

### Initial Setup (New Command: `init --with-recovery`)

```bash
$ ccmd init --with-recovery

=== CCMD Master Password Setup ===

Enter new master password: ********
Confirm password: ********

✓ Master password set successfully (using bcrypt)

=== Recovery Codes Generation ===

⚠️  IMPORTANT: Save these recovery codes in a safe place!

These codes can be used if you forget your master password.
Each code works only ONCE and will be deleted after use.

Your Recovery Codes:
┌────────────────────────┐
│ 1. A7F2-9K3L-P5Q8-R1T4 │
│ 2. B8G3-0M4N-Q6R9-S2U5 │
│ 3. C9H4-1N5O-R7S0-T3V6 │
│ 4. D0J5-2P6Q-S8T1-U4W7 │
│ 5. E1K6-3Q7R-T9U2-V5X8 │
│ 6. F2L7-4R8S-U0V3-W6Y9 │
│ 7. G3M8-5S9T-V1W4-X7Z0 │
│ 8. H4N9-6T0U-W2X5-Y8A1 │
│ 9. J5P0-7U1V-X3Y6-Z9B2 │
│ 10. K6Q1-8V2W-Y4Z7-A0C3 │
└────────────────────────┘

Print these codes? (y/n): y
✓ Recovery codes saved to: ~/ccmd_recovery_codes.txt

⚠️  Store these codes securely:
   • Print them and keep in a safe place
   • Store in password manager
   • Do NOT store them on the same device
   • Each code works only ONCE

✓ Setup complete!
```

---

### Using Recovery Code (Forgot Password Scenario)

```bash
$ ccmd sudo apt update

CCMD password: [user enters wrong password]
Incorrect password. 2 attempt(s) remaining.

CCMD password: [presses Ctrl+C]

→ Forgot your password? Use a recovery code instead.
→ Type 'recovery' or press Enter to try password again: recovery

=== Password Recovery ===

Enter recovery code: A7F2-9K3L-P5Q8-R1T4

✓ Recovery code accepted!
⚠️  This code has been used and deleted (9 codes remaining)
⚠️  Consider generating new recovery codes: ccmd change-password --regenerate-recovery

[command executes successfully]
```

---

### Managing Recovery Codes

#### View Remaining Codes
```bash
$ ccmd recovery-status

=== Recovery Codes Status ===

Total codes: 10
Used codes: 3
Remaining codes: 7

⚠️  You have 7 recovery codes remaining.

Commands:
  • Generate new codes: ccmd change-password --regenerate-recovery
  • View codes: ccmd show-recovery-codes (requires password)
```

#### Show Recovery Codes (Requires Password)
```bash
$ ccmd show-recovery-codes

CCMD password: ********

=== Your Recovery Codes ===

Remaining codes (7):
  1. B8G3-0M4N-Q6R9-S2U5
  2. C9H4-1N5O-R7S0-T3V6
  [... 5 more codes ...]

⚠️  Keep these codes secret and secure!
⚠️  Each code can only be used once.
```

#### Regenerate Recovery Codes
```bash
$ ccmd change-password --regenerate-recovery

CCMD password: ********

=== Regenerate Recovery Codes ===

⚠️  This will DELETE all existing recovery codes (7 remaining)
⚠️  You will receive 10 NEW recovery codes

Continue? (yes/no): yes

✓ Old recovery codes deleted
✓ New recovery codes generated:

Your New Recovery Codes:
┌────────────────────────┐
│ 1. M7N2-9P4Q-R6S8-T0U1 │
│ 2. N8O3-0Q5R-S7T9-U1V2 │
│ [... 8 more codes ...]  │
└────────────────────────┘

Print these codes? (y/n): y
✓ Recovery codes saved to: ~/ccmd_recovery_codes.txt
```

---

## Technical Implementation Design

### File Structure

**Location:** `~/.ccmd/recovery_codes.key`

**Format (JSON):**
```json
{
  "version": "1.2.0",
  "hash_method": "bcrypt",
  "codes": [
    {
      "id": 1,
      "hash": "$2b$12$...",
      "created_at": "2025-10-27T10:30:00Z",
      "used": false
    },
    {
      "id": 2,
      "hash": "$2b$12$...",
      "created_at": "2025-10-27T10:30:00Z",
      "used": false
    }
    // ... 8 more codes
  ]
}
```

### Code Generation Algorithm

```python
def generate_recovery_codes(count=10):
    """Generate cryptographically secure recovery codes"""
    import secrets
    import string

    codes = []
    charset = string.ascii_uppercase + string.digits

    for _ in range(count):
        # Generate 16 random characters
        code_chars = ''.join(secrets.choice(charset) for _ in range(16))

        # Format as XXXX-XXXX-XXXX-XXXX
        formatted = '-'.join([
            code_chars[0:4],
            code_chars[4:8],
            code_chars[8:12],
            code_chars[12:16]
        ])

        codes.append(formatted)

    return codes
```

### Code Verification Algorithm

```python
def verify_recovery_code(user_input):
    """Verify recovery code and mark as used"""
    # Load recovery codes
    codes_data = load_recovery_codes()

    # Normalize input (remove spaces/dashes)
    normalized_input = user_input.upper().replace('-', '').replace(' ', '')

    # Check each unused code
    for code_entry in codes_data['codes']:
        if code_entry['used']:
            continue

        # Verify hash
        if verify_code_hash(normalized_input, code_entry['hash']):
            # Mark as used
            code_entry['used'] = True
            code_entry['used_at'] = datetime.utcnow().isoformat()

            # Save immediately
            save_recovery_codes(codes_data)

            # Log the event
            log_recovery_code_use(code_entry['id'])

            return True, f"Code accepted ({count_remaining(codes_data)} remaining)"

    return False, "Invalid recovery code"
```

### Security Features

```python
# 1. Constant-time comparison (prevent timing attacks)
def verify_code_hash(code, stored_hash):
    if HAS_BCRYPT:
        return bcrypt.checkpw(code.encode(), stored_hash.encode())
    else:
        # PBKDF2 fallback
        return verify_pbkdf2(code, stored_hash)

# 2. Rate limiting (prevent brute force)
MAX_RECOVERY_ATTEMPTS = 3
RECOVERY_LOCKOUT_TIME = 300  # 5 minutes

# 3. Audit logging
def log_recovery_code_use(code_id):
    """Log recovery code usage for security audit"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': 'recovery_code_used',
        'code_id': code_id,
        'username': os.getlogin(),
        'ip': get_client_ip(),
    }
    append_to_audit_log(log_entry)
```

---

## Security Considerations

### ✅ Strengths

1. **Cryptographically Random** - Uses `secrets` module (not `random`)
2. **Hashed Storage** - Codes never stored in plaintext
3. **Single-Use** - Each code immediately deleted after use
4. **Constant-Time Verification** - Prevents timing attacks
5. **Audit Logging** - All recovery code usage logged
6. **Rate Limiting** - Prevents brute force attempts
7. **Secure Permissions** - 0600 file permissions

### ⚠️ Important Warnings

1. **Physical Security** - User must secure printed codes
2. **No Recovery from Total Loss** - If password AND all codes lost, account is unrecoverable
3. **Social Engineering** - User education about not sharing codes
4. **Backup Burden** - User responsible for storing codes safely

### 🔒 Best Practices (Documented for Users)

1. **Print codes** and store in safe/lockbox
2. **Use password manager** as backup location
3. **Never email** codes to yourself
4. **Regenerate codes** after using 3+ codes
5. **Don't store** codes on same device as CCMD
6. **Consider splits** - store 5 codes in location A, 5 in location B

---

## New Commands for v1.2.0

| Command | Description | Password Required | Interactive |
|---------|-------------|-------------------|-------------|
| `init --with-recovery` | Initialize with recovery codes | No | Yes |
| `recovery-status` | Show recovery codes status | No | No |
| `show-recovery-codes` | Display remaining codes | Yes | Yes |
| `change-password --regenerate-recovery` | Regenerate all codes | Yes | Yes |
| `disable-recovery` | Delete all recovery codes | Yes | Yes |

---

## Migration Path (v1.1.x → v1.2.0)

### Existing Users

```bash
$ ccmd init --add-recovery

You already have a master password set.
Do you want to add recovery codes? (y/n): y

CCMD password: ********

✓ Password verified
✓ Generating 10 recovery codes...

[Shows codes as in initial setup]
```

### Opt-Out

```bash
$ ccmd disable-recovery

⚠️  This will DELETE all recovery codes
⚠️  You will NOT be able to recover your password
⚠️  Are you sure? (type 'DELETE' to confirm): DELETE

CCMD password: ********

✓ All recovery codes deleted
✓ Recovery system disabled
```

---

## Alternative Approaches Considered

### ❌ Email-Based Recovery
- **Rejected:** Requires email server setup, adds complexity
- **Security Risk:** Email compromise = CCMD compromise

### ❌ Security Questions
- **Rejected:** Easily guessed/researched, poor security
- **Industry consensus:** Backup codes are superior

### ❌ Master Recovery Key
- **Rejected:** Single point of failure, all or nothing
- **Better:** Multiple single-use codes distributes risk

### ✅ Single-Use Backup Codes (Selected)
- **Industry Standard:** Used by GitHub, Google, Dropbox, etc.
- **Proven Security:** Battle-tested approach
- **User-Friendly:** Simple to understand and use
- **Secure by Default:** Each code is single-use

---

## Implementation Checklist (For v1.2.0)

### Core Functionality
- [ ] `generate_recovery_codes()` - Cryptographically secure generation
- [ ] `hash_recovery_code()` - bcrypt/PBKDF2 hashing
- [ ] `verify_recovery_code()` - Constant-time verification
- [ ] `mark_code_used()` - Immediate deletion after use
- [ ] `save_recovery_codes()` - Atomic file operations
- [ ] `load_recovery_codes()` - Secure file reading

### Commands
- [ ] `init --with-recovery` - Setup with codes
- [ ] `init --add-recovery` - Add codes to existing setup
- [ ] `recovery-status` - Show status
- [ ] `show-recovery-codes` - Display codes (password protected)
- [ ] `change-password --regenerate-recovery` - Regenerate
- [ ] `disable-recovery` - Opt-out

### Security
- [ ] Rate limiting (3 attempts, 5-minute lockout)
- [ ] Audit logging
- [ ] File permissions (0600)
- [ ] Constant-time comparison
- [ ] Input normalization (handle various formats)

### Testing
- [ ] Unit tests for code generation
- [ ] Unit tests for verification
- [ ] Unit tests for single-use enforcement
- [ ] Integration tests for recovery flow
- [ ] Security tests (timing attacks, brute force)

### Documentation
- [ ] User guide for recovery codes
- [ ] Security best practices
- [ ] Migration guide for v1.1.x users
- [ ] Troubleshooting guide

---

## Estimated Timeline

- **Design & Review:** 1 week (DONE - This document)
- **Implementation:** 2-3 weeks
- **Testing:** 1-2 weeks
- **Documentation:** 1 week
- **Beta Testing:** 2 weeks
- **Total:** ~7-9 weeks for v1.2.0 release

---

## Questions for Discussion

1. **Code Count:** Should we allow users to choose between 10, 15, or 20 codes?
2. **Format:** Is `XXXX-XXXX-XXXX-XXXX` the best format? (vs `XXXXXXXXXXXXXXXX`)
3. **Expiry:** Should codes expire after 6 months/1 year? (industry: usually no expiry)
4. **Warning Threshold:** Alert user when < 3 codes remaining?
5. **Export Format:** PDF, TXT, or both for printed codes?

---

## Feedback from Community

> **From Wisyle's Friend:**
> *"Allow backup codes to bypass TOTP if the user loses access. Each backup code is single-use; remove it from storage after use."*
>
> **Implementation:** ✅ Fully addressed in this design

> **Expected Use Case:**
> *"For those who plans to install CCMD in a large server base to automate and shorten extra long commands"*
>
> **Benefit:** Critical for enterprise/server deployments where password loss = system lockout

---

## Success Criteria

✅ User can recover access with recovery code
✅ Each code works exactly once
✅ Codes are cryptographically secure
✅ Zero-trust: codes stored hashed, never plaintext
✅ Clear warnings about code security
✅ Easy to understand and use
✅ No dependencies (works with/without bcrypt)

---

**Design Status:** ✅ Ready for Implementation in v1.2.0

**Next Step:** Review this mockup, gather feedback, then implement!

---

*Document Version: 1.0*
*Created: October 27, 2025*
*Author: De Catalyst (@Wisyle)*
