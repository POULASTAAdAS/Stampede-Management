# Quick License Guide - FIXED VERSION

## Problem FIXED ✓

The license activation was failing with "No license found" error. This has been **FIXED**.

## What Was Wrong

1. `license_generator_tool.py` used `'customer'` key, but `license_manager.py` expected `'customer_name'`
2. Signature generation algorithms didn't match

## What Was Fixed

- ✓ Fixed key name from `'customer'` to `'customer_name'`
- ✓ Fixed signature algorithm to use HMAC (matching validator)
- ✓ Fixed `generate_dev_license.py` to use correct method name
- ✓ Regenerated development license with correct format

## How to Use (Step-by-Step)

### For Administrators - Generating Customer Licenses

1. **Get Machine ID from Customer**
    - Customer runs the app and sees activation dialog
    - Customer clicks "Copy Machine ID" and sends it to you
    - Example: `76de26ca206943a91b617aedcb6d3ed6`

2. **Generate License**
   ```bash
   cd auth
   python license_generator_tool.py
   ```

3. **In the License Generator GUI:**
    - Paste the Machine ID into "Machine ID" field
    - (Optional) Enter MAC Address and Username if provided
    - Enter Customer Name (e.g., "anshu")
    - Set validity period (default: 365 days)
    - Click "Generate License"

4. **Copy the License**
    - Click "Copy to Clipboard"
    - The complete JSON license will be copied

5. **Send to Customer**
    - Email or send the complete JSON license key
    - Make sure to send the ENTIRE JSON block

### For Customers - Activating License

1. **Run the Application**
    - Launch CrowdMonitor.exe or run `python config_gui.py`
    - Activation dialog will appear

2. **Get Your Machine ID**
    - The dialog shows your Machine ID
    - Click "Copy Machine ID" if you need to send it to support

3. **Paste License Key**
    - Receive the license JSON from administrator
    - Paste the COMPLETE JSON into the text area:
   ```json
   {
     "machine_id": "76de26ca206943a91b617aedcb6d3ed6",
     "mac_address": "E8:48:B8:C8:20:00",
     "username": "root",
     "customer_name": "anshu",
     "created": "2026-02-04T02:12:54.916625",
     "expires": "2027-02-04T02:12:54.916598",
     "valid": true,
     "signature": "a282d915437c489847c12e16afd163dcc2b00978611b33644f99798cb02d468a"
   }
   ```

4. **Activate**
    - Click "Activate License"
    - Should show: "License activated successfully!"
    - App will now run normally

## Testing Your Setup

Run the test script to verify everything works:

```bash
python test_license_fix.py
```

Expected output:

```
ALL TESTS PASSED [OK]
The license generation and validation are now working correctly!
```

## For Developers

Generate your development license:

```bash
python generate_dev_license.py
```

This creates `auth/license.dat` valid for 365 days.

## Common Issues (Now Fixed)

### ❌ OLD PROBLEM: "No license found"

**Cause**: Signature mismatch between generator and validator
**Status**: ✓ FIXED in `license_generator_tool.py`

### ❌ OLD PROBLEM: "Invalid license signature"

**Cause**: Different signature algorithms
**Status**: ✓ FIXED - Now uses HMAC consistently

### ✓ NEW: Working Correctly

- License generation creates valid licenses
- License validation accepts generated licenses
- Signature verification works properly
- Machine ID matching works
- Expiration checking works

## File Structure

```
auth/
├── license_manager.py            # Core system (unchanged)
├── license_generator_tool.py     # FIXED - Now generates valid licenses
├── license.dat                   # Your license (regenerated)

Root/
├── generate_dev_license.py       # FIXED - Uses correct method name
├── test_license_fix.py          # NEW - Verification test
├── LICENSE_FIX_SUMMARY.md       # Technical details of fix
└── QUICK_LICENSE_GUIDE.md       # This file
```

## Summary

✓ **Issue Fixed**: License generation and validation now work correctly
✓ **Tested**: All tests pass
✓ **Ready to Use**: Generate licenses using `license_generator_tool.py`

## Need Help?

1. Run `python test_license_fix.py` to verify system is working
2. Check `LICENSE_FIX_SUMMARY.md` for technical details
3. See `README.md` for general usage information
