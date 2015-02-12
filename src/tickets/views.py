from datetime import datetime, timezone
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from tickets.models import TicketCode, Attempt, FakeAttempt, MAX_CODE_LENGTH, MAX_FAKE_CODE_LENGTH, \
    TicketCodeSerializer, AttemptSerializer
from django.contrib.auth.decorators import permission_required


HTTP_STATUS_DISABLED = 471
HTTP_STATUS_USED = 470


@permission_required('tickets.add_attempt')
def attempt(request, code):
    try:
        if len(code) > MAX_CODE_LENGTH:
            code = code[:MAX_FAKE_CODE_LENGTH]
            raise TicketCode.DoesNotExist("Code '{}' does not exist".format(code))
        at, item = TicketCode.objects.make_attempt(code=code, user=request.user)
    except TicketCode.DoesNotExist:
        at = FakeAttempt(code=code)
        at.save(request=request)
        response = render_to_response('tickets/attempt/404.html', {'code': code})
        response.status_code = 404
        return response
    except Exception as e:
        return HttpResponseServerError("Error saving attempt" + e.message)

    context = {'code': code}

    if not at:
        return render_attempt(request, context, HTTP_STATUS_DISABLED)

    context['code'] = item
    if at.success:
        return render_attempt(request, context, status.HTTP_201_CREATED)

    context['attempts'] = item.attempt_list.order_by('-id').all()
    return render_attempt(request, context, HTTP_STATUS_USED)


def render_attempt(request, context, status_code):
    return TemplateResponse(request,
                            'tickets/attempt/{}.html'.format(status_code),
                            context,
                            status=status_code)


class TicketCodeViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    """
    API endpoint that allows ticket code to be viewed.
    """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'code'
    queryset = TicketCode.objects.filter(ticket_pack__event__active=True).all()
    serializer_class = TicketCodeSerializer


class TicketCodeAttemptViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):

    """
    API endpoint that allows attempts to be viewed or created.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Attempt.objects.all()
    serializer_class = AttemptSerializer

    def get_queryset(self):
        ticket_code = TicketCode.objects.get(code=self.kwargs.get('code'),
                                             ticket_pack__event__active=True)
        queryset = super(TicketCodeAttemptViewSet, self).get_queryset()
        return queryset.filter(ticket_code=ticket_code).all()

    def create(self, request, *args, **kwargs):
        attempt, ticket_code = TicketCode.objects.make_attempt(kwargs.get('code'), request.user)

        if not attempt:
            return Response({'result': 'Code disabled',
                             'ticket_code': TicketCodeSerializer(ticket_code).data},
                            status=HTTP_STATUS_DISABLED)

        serializer = self.get_serializer(attempt)
        headers = self.get_success_headers(serializer.data)

        if attempt.success:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response(serializer.data, status=HTTP_STATUS_USED, headers=headers)

    def get_success_headers(self, data):
        headers = super(TicketCodeAttemptViewSet, self).get_success_headers(data)
        headers['Tarrabme-Server-DateTime'] = datetime.now(tz=timezone.utc)

        return headers

    def handle_exception(self, exc):
        if isinstance(exc, TicketCode.DoesNotExist):
            return Response({'result': exc.args[0],
                             'code': self.kwargs.get('code')},
                            status=status.HTTP_404_NOT_FOUND)

        return super(TicketCodeAttemptViewSet, self).handle_exception(exc)
