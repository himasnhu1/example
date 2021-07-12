from django.urls import path, re_path
from ubfcart.views import *

app_name = 'ubfcart'

urlpatterns = [
	path("add-to-cart/", AddToCartView.as_view()),
	path("remove-from-cart/", RemoveFromCartView.as_view()),
	path("add-to-bookmark/", AddToBookmarkView.as_view()),
	path("remove-from-bookmark/", RemoveFromBookmarkView.as_view()),
	path("save-for-later/", AddToSaveForLaterView.as_view()),
	path("remove-saved-for-later/", RemoveFromSavedForLaterView.as_view()),

	path("cart/", CartDetailView.as_view()),
	path("buy-now/", BuyNowView.as_view()),
	path("bookmarked/", BookmarkDetailView.as_view()),
	path("saved-for-later/", SaveForLaterDetailView.as_view()),

	path("orders/", UserOrdersView.as_view()),
	path("confirm-payment/", ConfirmPaymentView.as_view()),

	path("promocode-remove/",PromocodeRemove.as_view()),
	path("promocode-check/",PromocodeChecker.as_view()),
	path("promocode-list/",PromocodeListAPI.as_view()),
]