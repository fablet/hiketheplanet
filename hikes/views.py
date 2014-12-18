from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from hikes import models
from json import dumps


@csrf_exempt
def ajax(request):
    if request.method =="POST":
        region = models.Region()
        region.region = request.POST["region"]
        region.save()

    region_list = list(models.Region.objects.order_by('-num_hikes'))
    ajax_region_list = []
    for r in region_list:
        ajax_region_list.append({
            "region": r.region,
            "number of hikes": str(r.num_hikes),
        })

    return HttpResponse(dumps(ajax_region_list), content_type="application/json")


def index(request):
    context = RequestContext(request)
    region_list = models.Region.objects.order_by('-num_hikes')
    context_dict = {'regions': region_list}
    for region in region_list:
        region.url = encode_url(region.name)
    return render_to_response('hikes/index.html', context_dict, context)


def region(request, region_url):
    context = RequestContext(request)
    context_dict = build_context_dict(models.Region, region_url, 'region')

    try:
        this_region = models.Region.objects.get(name=context_dict['region'])
        trailheads = models.Trailhead.objects.filter(region=this_region).order_by('-latitude')
        context_dict['trailheads'] = trailheads
        context_dict['region'] = this_region
        for trailhead in trailheads:
            trailhead.url = encode_url(trailhead.name)
    except models.Region.DoesNotExist:
        pass

    return render_to_response('hikes/region.html', context_dict, context)


def trailhead(request, trailhead_url):
    context = RequestContext(request)
    context_dict = build_context_dict(models.Trailhead, trailhead_url, 'trailhead')

    try:
        this_location = models.Trailhead.objects.get(name=context_dict['trailhead'])
        hikes = models.Hike.objects.filter(trailhead=this_location)
        context_dict['trailhead'] = this_location
        context_dict['hikes'] = hikes
        for hike in hikes:
            hike.url = encode_url(hike.name)
    except models.Region.DoesNotExist:
        pass

    return render_to_response('hikes/trailheads.html', context_dict, context)


def hike(request, hike_url):
    context = RequestContext(request)
    context_dict = build_context_dict(models.Hike, hike_url, 'hike')
    hike_details = models.Hike.objects.get(name=context_dict['hike'])
    context_dict['hike'] = hike_details
    return render_to_response('hikes/hike.html', context_dict, context)

def register(request):
    context = RequestContext(request)
    registered = False

    pass


def encode_url(name):
    to_keep = 'abcdefghijklmnopqrstuvwxyz '
    lower_name = name.lower()
    clean_name = lower_name
    for char in lower_name:
        if char not in to_keep:
            clean_name = lower_name.replace(char, '')
    clean_name = clean_name.replace('  ', ' ')
    return clean_name.replace(' ', '_')


def decode_url(url, field_list):
    url_name = url.replace('_', ' ')
    url_name = url_name.title()
    for name in field_list:
        if name.startswith(url_name[:6]):
            if url == encode_url(name):
                return name
    return url_name


def build_context_dict(this_model, url, key):
    names_list = this_model.objects.values_list('name', flat=True)
    this_name = decode_url(url, names_list)
    return {key: this_name}