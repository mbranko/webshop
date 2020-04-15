from mainshop.models import Customer


def jwt_response_payload_handler(token, user=None, request=None):
    try:
        customer = Customer.objects.get(user_id__exact=user.id)
        roles = ['staff'] if user.is_staff else []
        user_data = {
            'id': customer.id,
            'email': customer.user.email,
            'firstName': customer.user.first_name,
            'lastName': customer.user.last_name,
            'isStaff': customer.user.is_staff,
            'address': customer.address,
            'city': customer.city,
            'zipCode': customer.zip_code,
            'roles': roles,
            'token': token
        }
    except Customer.DoesNotExist:
        user_data = {
            'id': user.id,
            'token': token
        }
    return user_data
