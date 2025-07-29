# Subscription Controls Documentation

## Overview

The `subscription/controls.py` file contains two main control classes that handle subscription management and payment processing for a Django-based subscription system. This system supports multiple partners including CIPRES, CyVerse, and TAIR, with integration to Stripe for payment processing.

## Classes and Their Responsibilities

### 1. SubscriptionControl Class

#### Purpose

Manages subscription lifecycle, user bucket usage tracking, and page access tracking.

#### Key Methods

##### User Bucket Usage Management

- **`createOrUpdateUserBucketUsage(partyId, units)`**

  - Creates new or updates existing user bucket usage records
  - Sets expiry date to 365 days from current date
  - Adds units to both total and remaining unit counts

- **`createOrUpdateUserBucketUsage_Free(partyId, units)`**
  - Similar to above but for free usage units
  - Prevents adding new free units until previous ones expire
  - Uses separate `free_expiry_date` field

##### Subscription Management

- **`createOrUpdateSubscription(partyId, partnerId, period)`**
  - Handles three scenarios:
    1. **New subscription**: Creates fresh subscription with start/end dates
    2. **Expired subscription**: Renews from current date
    3. **Active subscription**: Extends existing end date
  - Returns subscription object and transaction details

##### Page Tracking

- **`get_filtered_uri(full_uri)`**

  - Filters URIs to standardize tracking for specific endpoints
  - Handles special cases like Araport11, sequence viewers, and API endpoints

- **`checkTrackingPage(partyId, uri)`**

  - Checks if a page has been accessed within last 24 hours
  - Returns: "New", "Cached", or "Expired"

- **`cacheNewTrackingPage(partyId, uri)`**
  - Records new page access or updates existing timestamp
  - Implements 24-hour caching mechanism

### 2. PaymentControl Class

#### Purpose

Handles all payment processing, Stripe integration, email notifications, and partner-specific synchronization.

#### Partner-Specific Payment Methods

##### CIPRES Integration

- **`chargeForCIPRES(...)`**
  - Processes credit purchases for CIPRES computational resources
  - Creates/updates Stripe customers with billing information
  - Generates usage unit purchases and syncs with CIPRES API
  - Handles payment failures and sync failures with appropriate notifications

##### CyVerse Integration

- **`chargeForCyVerse(...)`**
  - Processes subscription and add-on purchases for CyVerse platform
  - Supports both tier subscriptions and add-on options
  - Syncs purchases with CyVerse API using CyVerseClient
  - Handles multiple add-ons in single transaction

##### TAIR Bucket System

- **`chargeForBucket(...)`**
  - Processes bucket-based credit purchases for TAIR
  - Creates activation codes for purchased buckets
  - Records bucket transactions with ORCID integration

##### Generic Phoenix Subscriptions

- **`tryCharge(...)`**
  - General-purpose subscription payment processing
  - Creates activation codes based on subscription terms
  - Handles standard Phoenix partner subscriptions

#### Supporting Methods

##### Database Operations

- **`createUnitPurchase(...)`** - Creates CIPRES usage unit purchase records
- **`createUsageTierPurchase(...)`** - Creates CyVerse tier purchase records
- **`createAddonPurchase(...)`** - Creates CyVerse add-on purchase records
- **`postPaymentHandling(...)`** - Generates activation codes for standard subscriptions
- **`postPaymentHandlingForBucket(...)`** - Generates activation codes for bucket purchases

##### Validation

- **`validateCharge(price, termId, quantity)`** - Validates payment amounts including group discounts
- **`isValidRequest(request, message)`** - Validates standard subscription requests
- **`isValidRequestBucket(request, message)`** - Validates bucket purchase requests

##### Pricing

- **`getTermPrice(termId)`** - Retrieves subscription term pricing
- **`getBucketPrice(bucketId)`** - Retrieves bucket pricing

##### Email System

The class includes comprehensive email functionality:

**Customer Notifications:**

- **`sendCIPRESEmail(...)`** - Sends purchase confirmations for CIPRES
- **`sendCyVerseEmail(...)`** - Sends purchase confirmations for CyVerse
- **`emailReceipt(...)` / `sendEmailForBucketPurchase(...)`** - Sends activation codes and receipts

**Admin Notifications:**

- **`sendCyVerseAdminEmail(...)`** - Notifies admins of successful CyVerse purchases
- **`sendCIPRESSyncFailedEmail(...)`** - Alerts admins to CIPRES sync failures
- **`sendCyVerseSyncFailedEmail(...)`** - Alerts admins to CyVerse sync failures
- **`sendCyVersePaymentErrorEmail(...)`** - Notifies tech team of payment failures

##### Utility Methods

- **`getEmailInfo(...)`** - Prepares email data for standard subscriptions
- **`getEmailInfoForBucketPurchase(...)`** - Prepares email data for bucket purchases
- **`createCyVerseStripeDescription(...)`** - Formats Stripe charge descriptions
- **`postAddonPurchase(...)`** - Syncs add-on purchases with CyVerse
- **`getExpirationDate(...)`** - Calculates subscription expiration dates
- **`logPaymentError(...)`** - Centralized error logging for payment issues

## Key Features

### Multi-Partner Support

- **CIPRES**: Computational biology platform with CPU hour purchases
- **CyVerse**: Cloud-based platform with tiered subscriptions and add-ons
- **TAIR**: Plant biology database with bucket-based credit system
- **Generic Phoenix**: Standard subscription model for other partners

### Payment Processing

- Stripe integration for credit card processing
- Customer creation and management
- Invoice generation with custom fields
- Comprehensive error handling for various Stripe error types

### Synchronization

- Real-time API synchronization with partner systems
- Fallback mechanisms for sync failures
- Automatic retry and manual resolution workflows

### Email Communications

- HTML email templates with partner branding
- Activation code delivery
- Purchase confirmations with detailed receipts
- Administrative notifications for monitoring

### Security and Validation

- Payment amount validation with discount support
- Request parameter validation
- Error logging and monitoring
- Secure handling of customer data

## Error Handling

The system implements robust error handling:

- Stripe API error categorization and user-friendly messages
- Partner API sync failure recovery
- Email delivery failure logging
- Payment validation and fraud prevention

## Database Models Used

- `UserBucketUsage` - Tracks user credit balances
- `Subscription` - Core subscription records
- `ActivationCode` - Generated codes for account activation
- `UsageUnitPurchase` - CIPRES credit purchases
- `UsageTierPurchase` - CyVerse subscription purchases
- `UsageAddonPurchase` - CyVerse add-on purchases
- `BucketTransaction` - TAIR bucket purchase records
- `UserTrackPages` - Page access tracking

## Integration Points

- **Stripe API**: Payment processing and customer management
- **CIPRES API**: Credit synchronization via `APICaller`
- **CyVerse API**: Subscription management via `CyVerseClient`
- **Django Email**: SMTP-based email delivery
- **Partner Systems**: Real-time synchronization for account provisioning

This file serves as the core business logic layer for the subscription management system, handling the complex workflows between payment processing, partner integration, and customer communication.
