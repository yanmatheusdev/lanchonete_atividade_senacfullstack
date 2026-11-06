from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Categoria, Produto


class CatalogApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="test-password",
        )
        self.categoria = Categoria.objects.create(
            nome="Lanches",
            descricao="Sanduíches",
        )
        self.produto = Produto.objects.create(
            nome="X-Burger",
            preco="18.00",
            categoria=self.categoria,
        )

    def authenticate(self):
        self.client.force_authenticate(self.user)

    def test_api_lists_products_with_category_name(self):
        response = self.client.get(reverse("produto-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["categoria_nome"], "Lanches")

    def test_product_filters_and_search(self):
        unavailable = Produto.objects.create(
            nome="X-Burger especial",
            preco="20.00",
            categoria=self.categoria,
            disponivel=False,
        )

        response = self.client.get(reverse("produto-list"), {"disponivel": "false"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data["results"]], [unavailable.id])

        response = self.client.get(reverse("produto-list"), {"search": "especial"})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], unavailable.id)

    def test_product_filter_rejects_invalid_boolean(self):
        response = self.client.get(reverse("produto-list"), {"disponivel": "yes"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_price_is_rejected(self):
        self.authenticate()
        response = self.client.post(
            reverse("produto-list"),
            {
                "nome": "Produto inválido",
                "preco": "-5",
                "disponivel": True,
                "categoria": self.categoria.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("preco", response.data)

    def test_category_products_action_only_returns_its_products(self):
        another_category = Categoria.objects.create(nome="Bebidas")
        Produto.objects.create(
            nome="Suco",
            preco="8.00",
            categoria=another_category,
        )

        response = self.client.get(
            reverse("categoria-produtos", args=[self.categoria.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], self.produto.id)

    def test_category_with_products_cannot_be_deleted(self):
        self.authenticate()
        response = self.client.delete(
            reverse("categoria-detail", args=[self.categoria.id])
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("detalhe", response.data)

    def test_writes_require_authentication_and_token_allows_them(self):
        data = {"nome": "Bebidas", "descricao": "Bebidas geladas"}
        response = self.client.post(reverse("categoria-list"), data)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

        user = get_user_model().objects.create_user(
            username="api-user",
            password="test-password",
        )
        response = self.client.post(
            reverse("api-token"),
            {"username": user.username, "password": "test-password"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {response.data['token']}"
        )

        response = self.client.post(reverse("categoria-list"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("cardapio.services.requests.get")
    def test_municipalities_endpoint_normalizes_uf(self, get):
        response_from_ibge = Mock()
        response_from_ibge.json.return_value = [
            {"id": 2600054, "nome": "Abreu e Lima"}
        ]
        get.return_value = response_from_ibge

        response = self.client.get(reverse("municipio-list"), {"uf": "pe"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "uf": "PE",
            "total": 1,
            "municipios": [{"id": 2600054, "nome": "Abreu e Lima"}],
        })

    @patch("cardapio.services.requests.get")
    def test_municipalities_endpoint_rejects_missing_or_invalid_uf(self, get):
        for params in ({}, {"uf": "XX"}):
            with self.subTest(params=params):
                response = self.client.get(reverse("municipio-list"), params)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        get.assert_not_called()

    @patch("cardapio.services.requests.get", side_effect=requests.Timeout)
    def test_ibge_outage_returns_service_unavailable(self, get):
        response = self.client.get(reverse("municipio-list"), {"uf": "PE"})

        self.assertEqual(
            response.status_code,
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @patch("cardapio.serializers.municipality_exists", return_value=False)
    def test_delivery_area_rejects_unknown_ibge_code(self, municipality_exists):
        user = get_user_model().objects.create_user(
            username="area-user",
            password="test-password",
        )
        self.client.force_authenticate(user)

        response = self.client.post(
            reverse("area-entrega-list"),
            {
                "municipio": "Município inexistente",
                "codigo_ibge": 9999999,
                "taxa_entrega": "5.00",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Código IBGE inexistente.", response.data["codigo_ibge"])

    def test_swagger_documentation_is_available(self):
        response = self.client.get("/api/docs/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
