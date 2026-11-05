
import logging

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status

from .models import JobAnalysis
from .risk_engine import analyze_job_risk
from .nlp_analyzer import analyze_job_text
from .company_verifier import verify_company


logger = logging.getLogger(__name__)


def clean_text(value):
    """Return trimmed text, or an empty string for invalid input."""
    if not isinstance(value, str):
        return ""
    return value.strip()


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def analyze_job(request):

    job_title = clean_text(request.data.get('job_title'))
    company_name = clean_text(request.data.get('company_name'))
    job_description = clean_text(request.data.get('job_description'))

    if not job_title or not company_name or not job_description:
        return Response(
            {
                "error": "Job title, company name and job description are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(job_title) > 200:
        return Response(
            {"error": "Job title cannot exceed 200 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(company_name) > 200:
        return Response(
            {"error": "Company name cannot exceed 200 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(job_description) > 20000:
        return Response(
            {"error": "Job description cannot exceed 20,000 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        risk_score, risk_level, risk_factors = analyze_job_risk(
            job_description
        )

        nlp_insights = analyze_job_text(job_description)

        company_verification = verify_company(
            company_name,
            job_description
        )

        analysis = JobAnalysis.objects.create(
            user=request.user,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            risk_score=risk_score,
            risk_level=risk_level
        )

    except Exception:
        logger.exception("Job analysis failed.")
        return Response(
            {
                "error": "Something went wrong while analyzing this job. Please try again."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            "message": "Job analyzed successfully!",
            "analysis_id": analysis.id,
            "job_title": analysis.job_title,
            "company_name": analysis.company_name,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "nlp_insights": nlp_insights,
            "company_verification": company_verification
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def analysis_history(request):

    analyses = JobAnalysis.objects.filter(
        user=request.user
    ).order_by('-created_at')

    history = []

    for analysis in analyses:
        history.append({
            "id": analysis.id,
            "job_title": analysis.job_title,
            "company_name": analysis.company_name,
            "risk_score": analysis.risk_score,
            "risk_level": analysis.risk_level,
            "created_at": analysis.created_at.strftime(
                "%d-%m-%Y %H:%M"
            )
        })

    return Response(history, status=status.HTTP_200_OK)


# Retrieve one previously saved analysis
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def analysis_detail(request, analysis_id):

    try:
        analysis = JobAnalysis.objects.get(
            id=analysis_id,
            user=request.user
        )

    except JobAnalysis.DoesNotExist:
        return Response(
            {"error": "Analysis not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        # Regenerate risk factors from the saved description
        _, _, risk_factors = analyze_job_risk(
            analysis.job_description
        )

        # Regenerate NLP insights
        nlp_insights = analyze_job_text(
            analysis.job_description
        )

        # Regenerate company checks
        company_verification = verify_company(
            analysis.company_name,
            analysis.job_description
        )

    except Exception:
        logger.exception("Historical analysis retrieval failed.")

        return Response(
            {"error": "Unable to retrieve this analysis."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            "analysis_id": analysis.id,
            "job_title": analysis.job_title,
            "company_name": analysis.company_name,
            "risk_score": analysis.risk_score,
            "risk_level": analysis.risk_level,
            "risk_factors": risk_factors,
            "nlp_insights": nlp_insights,
            "company_verification": company_verification
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
def register_user(request):

    name = clean_text(request.data.get('name'))
    email = clean_text(request.data.get('email')).lower()
    password = request.data.get('password')

    if not name or not email or not password:
        return Response(
            {
                "error": "Name, email and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(password, str):
        return Response(
            {"error": "Password must be valid text."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(name) > 150:
        return Response(
            {"error": "Name cannot exceed 150 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(email) > 254:
        return Response(
            {"error": "Email cannot exceed 254 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"error": "Please enter a valid email address."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username__iexact=email).exists():
        return Response(
            {
                "error": "An account with this email already exists."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    temporary_user = User(
        username=email,
        email=email,
        first_name=name
    )

    try:
        validate_password(password, user=temporary_user)
    except ValidationError as error:
        return Response(
            {"error": list(error.messages)},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )

            token = Token.objects.create(user=user)

    except Exception:
        logger.exception("User registration failed.")
        return Response(
            {
                "error": "Unable to create your account right now. Please try again."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(
        {
            "message": "Account created successfully!",
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email,
            "token": token.key
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
def login_user(request):

    email = clean_text(request.data.get('email')).lower()
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {
                "error": "Email and password are required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if not isinstance(password, str):
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        username=email,
        password=password
    )

    if user is None:
        return Response(
            {
                "error": "Invalid email or password."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    token, created = Token.objects.get_or_create(user=user)

    return Response(
        {
            "message": "Login successful!",
            "token": token.key,
            "user_id": user.id,
            "name": user.first_name,
            "email": user.email
        },
        status=status.HTTP_200_OK
    )
