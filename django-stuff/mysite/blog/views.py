from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import generic
from .models import Post
from .forms import CommentForm, UserUpdateForm, ProfileUpdateForm
from django.shortcuts import render, get_object_or_404, redirect
from .recognize import train


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'index.html'
    paginate_by = 3


def post_detail(request, slug):
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None

    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        # comment_form.cleaned_data['name'] = request.user.username
        # comment_form.cleaned_data['email'] = request.user.email

        if comment_form.is_valid():

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)

            new_comment.name = request.user.username
            new_comment.email = request.user.email
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form})


def sign_up(request):
    if request.method == 'POST':
        username = request.POST['username']
        name = request.POST['name']
        surname = request.POST['surname']
        email = request.POST['email']
        password = request.POST['password']

        # if user is taken
        if User.objects.filter(username=username).exists():
            return render(request, 'auth/signup.html', {'user_taken': 'This Username is already taken.'})
        # if mail is taken
        if User.objects.filter(email=email).exists():
            return render(request, 'auth/signup.html', {'email_taken': 'This Email is already taken'})

        user = User.objects.create_user(username, email, password)
        user.first_name = name
        user.last_name = surname
        user.save()

        if user is not None:
            login(request, user)

            u_form = UserUpdateForm(instance=user)
            p_form = ProfileUpdateForm(instance=user.profile)

            context = {
                "user": user,
                "u_form": u_form,
                "p_form": p_form,
            }
            return render(request, 'profile.html', context)
        else:
            return render(request, 'auth/signup.html', {'unseen_error': 'Sorry you could not be registered :('})
    else:
        return render(request, 'auth/signup.html')


def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

            u_form = UserUpdateForm(instance=user)
            p_form = ProfileUpdateForm(instance=user.profile)

            context = {
                "user": user,
                "u_form": u_form,
                "p_form": p_form,
            }
            return render(request, 'profile.html', context)
        else:
            return render(request, 'auth/login.html', {"message": "Invalid Username or Password!"})
    else:
        return render(request, 'auth/login.html')


def log_out(request):
    logout(request)
    return redirect('/')


def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        old_image = request.POST['user_image']

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            # messages.success(request, f'Your account has been updated!')
            if old_image != p_form['image'].value():
                train.retrain(p_form['image'].value(), request.user.username)

            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "user": request.user,
        "u_form": u_form,
        "p_form": p_form,
    }

    return render(request, 'profile.html', context)

