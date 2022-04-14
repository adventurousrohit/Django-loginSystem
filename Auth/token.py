from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self,user,timestamps):
        return(
            text_type(user.pk) + text_type(timestamps)
        )

generate_token = TokenGenerator()