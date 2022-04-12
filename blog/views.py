from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, PostForm
from .models import Post, Author, PostView
from marketing.models import Signup


def get_user_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q') # usamos el metodo "GET" para obtener el valor por la url, per otmb se puede por el "POST"
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct() # si el resultado de los 2 filtros es el mismo, solo llame a uno que no sea igual 
    context = {
        'queryset': queryset
    }
    return render(request, 'blog/search_results.html', context)

def get_category_count():
    # nos retorna soo el campo de categoria de cada "post"
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories')) # annotate devuelve un diccionario donde cada clave sera cada categoria, y "count" para saber la cantidad de publicaciones que tiene esa categoria
    return queryset

@login_required
def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[:3]

    if request.method == "POST":
        email = request.POST['email'] # obtendremos el email por el nombre del atributo....
        new_signup = Signup() # llamamos una instanacia del modelo
        new_signup.email = email # le inyectamos el valor, pq el otro es automatico
        new_signup.save() # guardamos

    context = {
        'featured': featured,
        'latest': latest
    }
    return render (request, 'blog/index.html', context)

def blog(request):
    category_count = get_category_count() #traemos la funcion de mas arriba
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4) # pasamos queryset y cantidad de instancias por pagina
    page_request_var = 'page' # nombre de la variable que contiene el numero de la pagina en la que estamos
    page = request.GET.get(page_request_var) # obtener el numero de pagina.
    try:
        paginated_queryset = paginator.page(page) # nos devuelve la instancia de la pagina numero "page"
    except PageNotAnInteger: # le asignamos esta escepcion si no es un numero la pagina
        paginated_queryset = paginator.page(1) # si se ingresa un string, nos devuelve a la primera pagina
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages) # nos retorna el numero de paginas total de paginas, y nos redirige a la ultima

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count
    }
    return render (request, 'blog/blog.html', context)

def post(request, id):
    category_count = get_category_count() 
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse('post', args=str(post.id)))
            # post.get_absolute_url() # con este se Queda en al misma pagina, con los valores precargados que ya enviamos y si recargamos repite el comentario
    context = {
        'form': form,
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count
    }
    return render (request, 'blog/post.html', context)

def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_user_author(request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = request.user.author
            # form.instance.author = author
            form.save()
            return redirect(reverse('post', args=str(form.instance.id)))
    context = {
        'title': 'Create',
        'form': form
    }
    return render(request, 'blog/post_create.html', context)

def post_update(request, id):
    post= get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    author = get_user_author(request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = request.user.author
            # form.instance.author = author
            form.save()
            return redirect(reverse('post', args=str(form.instance.id)))
    context = {
        'title': 'Update',
        'form': form
    }
    return render(request, 'blog/post_create.html', context)

def post_delete(request, id):
    post= get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse('blog'))
