from rest_framework.throttling import ScopedRateThrottle

#Throttle for login endpoint
class LoginThrottle(ScopedRateThrottle):
    scope = "login"

#Throttle for password reset requests
class PasswordResetThrottle(ScopedRateThrottle):
    scope = "password_reset"

#Throttle for invitation acceptance
class InvitationAcceptThrottle(ScopedRateThrottle):
    scope = "invitation_accept"

#Throttle for product claim endpoint
class ProductClaimThrottle(ScopedRateThrottle):
    scope = "product_claim"
