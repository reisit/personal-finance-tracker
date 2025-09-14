from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from django.contrib import messages
from django.contrib.messages import get_messages
from django.views.decorators.http import require_POST
from .models import Users
from .forms import *
from App.functions.DAO import *
from App.functions.visuals import *
from App.functions.analysis import *
import matplotlib
matplotlib.use('Agg')

# Create your views here.
def home(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = Users.objects.get(username=username, password=password)
                return redirect('dashboard', seed=user.seed)
            except Users.DoesNotExist:
                messages.error(request, 'Invalid user or password')
    else:
        form = LoginForm()
    
    storage = get_messages(request)
    login_errors = [m for m in storage if m.level_tag == 'error']

    return render(request, 'home.html', {'login': form, 
                                         'login_errors': login_errors})
    

def register(request):
    if request.method == 'POST':
        form = RegForm(request.POST)
        if form.is_valid():

            u = form.cleaned_data['username']
            if Users.objects.filter(username=u).exists():
                form.add_error('username', 'Username already taken')
            
            else:
                data = form.cleaned_data        

                user = Users.objects.create(
                    name=data['name'],
                    lastName=data['lastName'],
                    username=data['username'],
                    password=data['password']
                )  

                print(user)     
                return redirect('home')
    else:
        form = RegForm()

    return render(request, 'register.html', {'register': form})

@cache_page(60 * 5)
def graphic_png(request, kind, seed):
    user = get_object_or_404(Users, seed=seed)
    
    mapping = {
        'balance':        balancePlot,
        'nextMonths':     nextMonths,
        'monthlyTrends':  monthlyTrends,
        'categories':     categoryDistribution,
    }
    plot_func = mapping.get(kind)
    if not plot_func:
        return HttpResponse(status=404)

    b64  = plot_func(user.seed)
    img  = base64.b64decode(b64)
    return HttpResponse(img, content_type='image/png')

def avgExpenseData(request, dwmy, seed):
    try:
        data = avgExpenses(request = request, dwmy = dwmy, seed = seed)
        return data
    except ValueError as e:
        return JsonResponse({'Error': str(e)}, status=400)
    
def freq_categories_image(request, seed):
    income  =  request.GET.get('income') == '1'
    expense =  request.GET.get('expense') == '1'
    try:
        data = mostFrequent(income= income, expense = expense, seed = seed)
        return data
    except ValueError as e:
        return JsonResponse({'Error': str(e)}, status=400)
    
def monthly_summary_image(request,seed):
    try:
        data = monthlySummary(seed = seed)
        return data
    except ValueError as e:
        return JsonResponse({'Error': str(e)}, status = 400)
    
@require_POST
def category_predict_api(request, seed):
    try:
        data = json.loads(request.body)

        desc = data.get('desc', '').strip()
        #seed = data.get('seed') 
        if not desc or not seed:
            return HttpResponseBadRequest('No description')
        category = categoryPredict(desc, seed)
        return JsonResponse({'category': 'Income' if category == 'I' else 'Expense'})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@require_POST
def amount_predict_api(request, seed):
    date_str = request.POST.get('date')
#   print(seed)
#   print(date_str)
#   print(f'ExpensePredictor(modelFilename={seed}.pkl, seed = {seed})')
    predictor = ExpensePredictor(modelFilename=f'{seed}.pkl', seed = seed)
    predictor.trainModel()
    try:
        dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
#       print(dt.day, dt.month)
        result = predictor.predict(day=dt.day, month=dt.month)
#       print(result)
        return JsonResponse({'prediction': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status = 400)

def dashboard_view(request, seed):
    try:
        user = Users.objects.get(seed=seed)
        print(request)

        insert_form = InsertForm()
        update_form = UpdateForm()
        delete_form = DeleteForm()

        if request.method == 'POST':
            action = request.POST.get('action')
            print("POST recibido:", request.POST)
            
            if action == 'insert':
                insert_form = InsertForm(request.POST)
                if insert_form.is_valid():
                    data = insert_form.cleaned_data
                    insert_transaction(data, seed)
                    messages.success(request, "Transacción insertada correctamente.")
                    return redirect('dashboard', seed=seed)

            elif action == 'update':
                update_form = UpdateForm(request.POST)
                if update_form.is_valid():
                    data = update_form.cleaned_data
                    update_transaction(data, seed)
                    messages.success(request, "Transacción actualizada correctamente.")
                    return redirect('dashboard', seed=seed)
                else:
                    print("Errores del formulario:", update_form.errors)

            elif action == 'delete':
                delete_form = DeleteForm(request.POST)
                if delete_form.is_valid():
                    data = delete_form.cleaned_data
                    delete_transaction(data, seed)
                    messages.success(request, "Transacción eliminada correctamente.")
                    return redirect('dashboard', seed=seed)

        df = getDf(seed)
        df = df.rename(columns={'id': 'Id'})
        transactions = df.to_dict(orient='records')

        try:
            tableSpendingDays = topSpendingDays(seed)
        except ValueError as e:
            tableSpendingDays = f"<div class='alert alert-warning'> {e} </div> "
        
        graphics = {
            'balance':              balancePlot(seed),
            'nextMonths':           nextMonths(seed),
            'monthlyTrends':        monthlyTrends(seed),
            'categories':           categoryDistribution(seed),
        } 

        print(seed,Balance(seed))

        context = {
            'user':                 user,
            'insert_form':          insert_form,
            'update_form':          update_form,
            'delete_form':          delete_form,
            'transactions':         transactions,
            'graphics':             graphics,
            'accumulatedBalance':   Balance(seed),
            'topSpendingDays':      tableSpendingDays,
            'seed':                 seed,
        }
        return render(request, 'dashboard.html', context)

    except Users.DoesNotExist:
        return render(request, 'error.html', {'message': 'Usuario no encontrado'})
