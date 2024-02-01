django has the default email backend service like the SMTP protocol used for email

configure the email backend completely

and then also add the REST_FRAMEWORK's configuration

then the JWT also has to be configured with simple JWT.

also add the corsheader middleware before the common middleware

and do remember that the middleware is also applied to outgoing response

**@property**
we use the @property when we want to like make the certain method as property and access it directly.

**password masking**
this ensures that the password is masked from the user

```
style={'input_type':'password'}
```

**a way to access the user from the context**

```
        user=self.context.get('user')

```

because the user.save() is called after the validate method,
we can calle the save method inside the validate method itself.

setting up the email service with email address and password will allow the to send custom email.
there is the default smtp service in django to send email.
