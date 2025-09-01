from django.utils.deprecation import MiddlewareMixin

from .models import ClickCounter


class ReferralMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'GET' and 'ref' in request.GET:
            token = request.GET['ref']
            try:
                referral = ClickCounter.objects.get(token=token)
                referral.clicks += 1
                referral.save()
                response = self.get_response(request)
                return response
            except ClickCounter.DoesNotExist:
                pass

        return self.get_response(request)
