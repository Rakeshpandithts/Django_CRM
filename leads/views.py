from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm,AssignAgentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Lead, Agent, Category
from agents.mixin import OrganisorAndLoginRequiredMixin
from django.core.mail import send_mail
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organiser:
            queryset = Lead.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation
            )

        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class CategoryDetailView(LoginRequiredMixin, DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organiser:
            queryset = Category.objects.filter(
                organisation=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                organisation=user.agent.organisation
            )
        return queryset


class SignupView(CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm
    def get_success_url(self):
        return reverse("login")

class LandingPageView(TemplateView):
    template_name = "landing.html"


class LeadListView(LoginRequiredMixin, ListView):
    # model = ModelName
    template_name='leads/leads_list.html'
    context_object_name = 'leads'
    def get_queryset(self):
        user = self.request.user
        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile,agent__isnull=True)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)


            queryset = queryset.filter(agent__user=user)
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_organiser:
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=True)
            context.update({
                "unassigned_leads": queryset
            })
        return context
    


class LeadDetailView(LoginRequiredMixin, DetailView):
    # model = ModelName
    template_name='leads/leads_detail.html'
    queryset = Lead.objects.all()
    context_object_name = 'lead'

class LeadCreateView(OrganisorAndLoginRequiredMixin, CreateView):
    # model = Model
    template_name = "leads/leads_create.html"
    form_class = LeadModelForm
    def get_success_url(self):
        return reverse("leads:lead-list")
    def form_valid(self, form):
        send_mail(subject = 'A lead has been created', 
        message = 'go to site to see new lead',
        from_email = 'test@test.com',
        recipient_list = ['test2@test.com'])
        return super(LeadCreateView, self).form_valid(form)



class LeadUpdateView(OrganisorAndLoginRequiredMixin, UpdateView):
    # model = Lead
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)
    def get_success_url(self):
        return reverse("leads:lead-list")
    


class LeadDeleteView(OrganisorAndLoginRequiredMixin, DeleteView):
    template_name = "leads/leads_delete.html"
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile)
    def get_success_url(self):
        return reverse("leads:lead-list")

class AssignAgentView(OrganisorAndLoginRequiredMixin, FormView):
    template_name = 'leads/assign_agent.html'
    form_class = AssignAgentForm
    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update( {
            "request": self.request
        })
        return kwargs
    def get_success_url(self):
        return reverse("leads:lead-list")
    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id = self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)
# Create your views here.
def landing_page(request):
    return render(request, 'landing.html') 



def lead_list(request):
    # return HttpResponse('Ganesha')
    leads = Lead.objects.all()
    print(leads)
    context = {
        'leads': leads
    }
    return render(request, 'leads/leads_list.html', context) 

def lead_detail(request, pk):

    lead = Lead.objects.get(id = pk)
    context= {
        'lead': lead
    }
    return render(request, 'leads/leads_detail.html', context) 

def lead_create(request):
    print(request.POST)
    form = LeadModelForm()
    if request.method == "POST":
        print("Receiving a post request")
        form = LeadModelForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            print('Lead has been created')

            return redirect('/leads')

    context= {
        "form": form
    }
    return render(request, 'leads/leads_create.html', context)

def lead_update(request, pk):
    lead = Lead.objects.get(id = pk)
    form = LeadModelForm(instance = lead)

    if request.method == "POST":
        form = LeadModelForm(request.POST, instance = lead)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            print('Lead has been created')
            return redirect('/leads')
    context= {
        'form': form,
        'lead': lead
    }
    return render(request, 'leads/lead_update.html', context) 

def lead_delete(request, pk):
    lead = Lead.objects.get(id = pk)
    lead.delete()
    return redirect('/leads')