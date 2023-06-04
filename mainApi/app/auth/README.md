## Auth

###Authentication

####Create User
- Requires email and password.
- Password is stored as hash
- otp_secret is saved in db and must also be saved by client.
- otp_secret can be saved by client by using the given otp_uri to create a QR code.
- The QR code can then be read using a mobile Authenticator App, 
which saved the otp_secret and is able to generate TOTP to allow the user to login


###Login 2FA - 2-factor Authentication

- Using email, password and TOTP

    ####TOTP - Time-based One-Time Password
    - 6 digits
    - valid for 30s
    - Most easily created by using an app that also stores the otp_secret
    - Using python you can run the following command to obtain a TOTP
      
    
    import pyotp
    
    otp = pyotp.TOTP(<otp_secret>)
    totp_code = otp.now()


###Authorization
- uses **OAuth2** with a bearer token
- token is obtained when creating a new user or when logging in
- token has a 30 minutes validity, but can be renewed indefinitely using the renew_token endpoint.
- all endpoints require that the user supplies an unexpired and valid token in their header
- Some endpoints might require the user to have additional permissions

