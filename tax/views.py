from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
# from models import ORC

class ORCImg(views.APIView):
    def get(self, request, *args, **kwargs):
        path = request.query_params.get('path')

        # ORC();

        return Response({"location": 'test-1304530197.cos.ap-guangzhou.myqcloud.com/return.xlsx'})

    def post(self, request, *args, **kwargs):
        path = request.data
        print(request.data)
        return Response({"location": 'test-1304530197.cos.ap-guangzhou.myqcloud.com/return.xlsx'})