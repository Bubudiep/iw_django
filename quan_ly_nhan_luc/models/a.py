from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from datetime import time
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
import random
import string