from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.functions import TruncMonth


def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)

    total = expenses.aggregate(Sum('amount'))['amount__sum']or 0

    category_data = expenses.values('category').annotate(total=Sum('amount'))

    labels = []
    data = []

    for item in category_data:
        labels.append(item['category'])
        data.append(float(item['total']))
        # Monthly chart
        monthly_data = (
            expenses
            .annotate(month=TruncMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        months = []
        month_totals = []

        for item in monthly_data:
            months.append(item['month'].strftime("%b"))
            month_totals.append(float(item['total']))

    context = {
        'expenses': expenses,
        'total': total,
        'labels': labels,
        'data': data
    }

    return render(request, 'expense/expense_list.html', context)


def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ExpenseForm()

    return render(request, 'expense/add_expense.html', {'form': form})

def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id)

    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'expense/edit_expense.html', {'form': form})

def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id)
    expense.delete()
    return redirect('/')



