from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book, BorrowRecord, CustomUser, Genre
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUserRole


# HTML page view
@login_required(login_url='/login/')
def admin_books_page(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("You are not allowed here.")
    return render(request, 'library/admin_books.html')


@login_required(login_url='/login/')
def home(request):
    return render(request, 'library/home.html')
def login_page(request):
    return render(request, 'library/login.html')

def register_page(request):
    return render(request, 'library/register.html')

# Get all available books
class BookListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        books = Book.objects.all().values('id', 'title', 'author', 'stock')
        return Response(list(books), status=status.HTTP_200_OK)

# Borrow a book
class IssueBookView(APIView):
    def post(self, request):
        book_id = request.data.get('book_id')
        user_id = request.data.get('user_id')

        try:
            book = Book.objects.get(id=book_id)
            user = CustomUser.objects.get(id=user_id)

            if book.stock < 1:
                return Response({'message': 'Book not available'}, status=status.HTTP_400_BAD_REQUEST)

            # Create record
            BorrowRecord.objects.create(
                borrower=user,
                book=book,
                due_date=timezone.now().date() + timedelta(days=7)
            )
            book.stock -= 1
            book.save()

            return Response({'message': 'Book issued successfully'}, status=status.HTTP_201_CREATED)

        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = authenticate(request, username=data['username'], password=data['password'])
        if user:
            login(request, user)
            return JsonResponse({'message': 'Login successful', 'user_id': str(user.id), 'role': user.role})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

@csrf_exempt
def register_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if CustomUser.objects.filter(username=data['username']).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        user = CustomUser.objects.create_user(
            username=data['username'],
            password=data['password'],
            role='member'
        )
        return JsonResponse({'message': 'User registered successfully', 'user_id': str(user.id)})

def logout_view(request):
    logout(request)
    return redirect('/login/')

class BorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        records = BorrowRecord.objects.filter(borrower=user).select_related('book')
        data = [{
            'id': record.id,
            'title': record.book.title,
            'borrowed_at': record.borrowed_at.strftime('%Y-%m-%d'),
            'due_date': record.due_date.strftime('%Y-%m-%d'),
            'returned_at': record.returned_at.strftime('%Y-%m-%d') if record.returned_at else None,
            'is_returned': record.is_returned
        } for record in records]
        return Response(data, status=200)
    
class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        record_id = request.data.get('record_id')
        try:
            record = BorrowRecord.objects.get(id=record_id, borrower=request.user)
            if record.is_returned:
                return Response({'message': 'Book already returned'}, status=400)

            record.is_returned = True
            record.returned_at = timezone.now()
            record.save()

            record.book.stock += 1
            record.book.save()

            return Response({'message': 'Book returned successfully'}, status=200)

        except BorrowRecord.DoesNotExist:
            return Response({'error': 'Record not found'}, status=404)
        
class AddBookView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request):
        data = request.data
        try:
            genre = Genre.objects.get(id=data.get('genre'))
            Book.objects.create(
                title=data.get('title'),
                author=data.get('author'),
                isbn=data.get('isbn'),
                genre=genre,
                stock=data.get('stock'),
                added_by=request.user
            )
            return Response({'message': 'Book added successfully'}, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=400)



        
class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        users = CustomUser.objects.exclude(id=request.user.id)
        data = [{
            'id': str(user.id),
            'username': user.username,
            'role': user.role,
        } for user in users]
        return Response(data, status=200)

class PromoteUserView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request):
        user_id = request.data.get('user_id')
        new_role = request.data.get('new_role')
        try:
            user = CustomUser.objects.get(id=user_id)
            user.role = new_role
            user.save()
            return Response({'message': f"{user.username} promoted to {new_role}"})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
@login_required(login_url='/login/')
def manage_roles_page(request):
    if not request.user.role == 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden("Only admins can access this page.")
    return render(request, 'library/user_roles.html')
class GenreListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        genres = Genre.objects.all().values('id', 'name')
        return Response(list(genres), status=200)
    
class BookDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def get(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            return Response({
                'id': str(book.id),
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'genre_id': book.genre.id if book.genre else None,
                'stock': book.stock
            }, status=200)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
class EditBookView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            genre = Genre.objects.get(id=request.data.get('genre'))

            book.title = request.data.get('title')
            book.author = request.data.get('author')
            book.isbn = request.data.get('isbn')
            book.genre = genre
            book.stock = request.data.get('stock')
            book.save()

            return Response({'message': 'Book updated successfully'}, status=200)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        except Genre.DoesNotExist:
            return Response({'error': 'Invalid genre'}, status=400)
        
class DeleteBookView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserRole]

    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            book.delete()
            return Response({'message': 'Book deleted successfully'}, status=200)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)


