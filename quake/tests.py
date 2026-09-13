from unittest.mock import patch, Mock

import requests
from django.contrib.auth.models import User
from django.test import TestCase

from .forms import EarthquakeSearchForm
from .models import History
from .views import PREFECTURE_COORDINATES, safe_float, safe_int


def make_usgs_response(features):
    """USGS Earthquake APIのレスポンスを模したMockを作る"""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'type': 'FeatureCollection', 'features': features}
    return response


def make_feature(place, mag=4.5, time_ms=1_600_000_000_000, lon=139.7, lat=35.7):
    return {
        'geometry': {'coordinates': [lon, lat, 10]},
        'properties': {'place': place, 'mag': mag, 'time': time_ms},
    }


class EarthquakeDataViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass12345')
        self.client.login(username='tester', password='pass12345')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get('/earthquake/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    @patch('quake.views.requests.get')
    def test_sends_prefecture_bbox_to_usgs(self, mock_get):
        mock_get.return_value = make_usgs_response([])

        self.client.get('/earthquake/', {'prefecture': '東京都'})

        expected = PREFECTURE_COORDINATES['東京都']
        _, kwargs = mock_get.call_args
        params = kwargs['params']
        self.assertEqual(params['minlatitude'], expected['minlat'])
        self.assertEqual(params['maxlatitude'], expected['maxlat'])
        self.assertEqual(params['minlongitude'], expected['minlon'])
        self.assertEqual(params['maxlongitude'], expected['maxlon'])

    @patch('quake.views.requests.get')
    def test_usgs_request_failure_does_not_crash_the_page(self, mock_get):
        # USGSへのリクエストが失敗（タイムアウト等）しても500エラーにならず、
        # 「0件ヒット」ではなく取得失敗である旨がテンプレートに伝わることを確認する
        mock_get.side_effect = requests.exceptions.Timeout('timed out')

        response = self.client.get('/earthquake/', {'prefecture': '東京都'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['all_earthquakes'], [])
        self.assertTrue(response.context['api_error'])
        self.assertContains(response, '地震データの取得に失敗しました')

    @patch('quake.views.requests.get')
    def test_no_matching_results_is_not_reported_as_api_error(self, mock_get):
        # APIは正常に応答したが該当件数が0件のケース。
        # api_error は立てず、「見つかりませんでした」の通常メッセージになることを確認する
        mock_get.return_value = make_usgs_response([])

        response = self.client.get('/earthquake/', {'prefecture': '東京都'})

        self.assertFalse(response.context['api_error'])
        self.assertContains(response, '該当する地震データが見つかりませんでした')

    @patch('quake.views.requests.get')
    def test_zenkoku_excludes_non_japan_results(self, mock_get):
        features = [
            make_feature('10km ESE of Ibaraki, Japan'),
            make_feature('50km SE of Busan, South Korea'),
        ]
        mock_get.return_value = make_usgs_response(features)

        response = self.client.get('/earthquake/', {'prefecture': '全国'})

        places = [eq['place'] for eq in response.context['all_earthquakes']]
        self.assertIn('10km ESE of Ibaraki, Japan', places)
        self.assertNotIn('50km SE of Busan, South Korea', places)

    @patch('quake.views.requests.get')
    def test_specific_prefecture_does_not_filter_by_place_text(self, mock_get):
        # 都道府県を指定した場合、APIへ渡すbboxで既に絞り込み済みのため
        # place文字列に「Japan」が含まれない結果でも除外されないことを確認する
        features = [make_feature('Near Tokyo Bay')]
        mock_get.return_value = make_usgs_response(features)

        response = self.client.get('/earthquake/', {'prefecture': '東京都'})

        places = [eq['place'] for eq in response.context['all_earthquakes']]
        self.assertIn('Near Tokyo Bay', places)

    @patch('quake.views.requests.get')
    def test_search_is_saved_to_history(self, mock_get):
        mock_get.return_value = make_usgs_response([])

        self.client.get('/earthquake/', {
            'year': '2021', 'min_magnitude': '4', 'max_magnitude': '6', 'prefecture': '大阪府',
        })

        self.assertEqual(History.objects.filter(user=self.user).count(), 1)
        history = History.objects.get(user=self.user)
        self.assertEqual(history.start_year, 2021)
        self.assertEqual(history.prefecture, '大阪府')
        self.assertEqual(history.min_magnitude, 4.0)
        self.assertEqual(history.max_magnitude, 6.0)

    @patch('quake.views.requests.get')
    def test_duplicate_search_within_same_minute_not_saved_twice(self, mock_get):
        mock_get.return_value = make_usgs_response([])
        params = {'year': '2021', 'min_magnitude': '4', 'max_magnitude': '6', 'prefecture': '大阪府'}

        self.client.get('/earthquake/', params)
        self.client.get('/earthquake/', params)

        self.assertEqual(History.objects.filter(user=self.user).count(), 1)

    @patch('quake.views.requests.get')
    def test_from_history_replay_does_not_create_history(self, mock_get):
        mock_get.return_value = make_usgs_response([])

        self.client.get('/earthquake/', {
            'year': '2021', 'prefecture': '大阪府', 'from_history': 'true',
        })

        self.assertEqual(History.objects.filter(user=self.user).count(), 0)

    @patch('quake.views.requests.get')
    def test_pagination_page_param_does_not_create_history(self, mock_get):
        mock_get.return_value = make_usgs_response([])

        self.client.get('/earthquake/', {'prefecture': '大阪府', 'page': '2'})

        self.assertEqual(History.objects.filter(user=self.user).count(), 0)


class DeleteHistoryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass12345')
        self.other_user = User.objects.create_user(username='other', password='pass12345')
        self.history = History.objects.create(
            user=self.other_user, start_year=2020, end_year=2020,
            min_magnitude=3.0, max_magnitude=7.0, prefecture='全国',
        )

    def test_requires_login(self):
        response = self.client.get(f'/history/delete/{self.history.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_cannot_delete_other_users_history(self):
        self.client.login(username='owner', password='pass12345')
        response = self.client.get(f'/history/delete/{self.history.id}/')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(History.objects.filter(id=self.history.id).exists())

    def test_can_delete_own_history(self):
        self.client.login(username='other', password='pass12345')
        response = self.client.get(f'/history/delete/{self.history.id}/')

        self.assertRedirects(response, '/mypage/')
        self.assertFalse(History.objects.filter(id=self.history.id).exists())


class EarthquakeSearchFormTest(TestCase):
    def test_valid_data(self):
        form = EarthquakeSearchForm(data={
            'year': '2020', 'min_magnitude': '3.0', 'max_magnitude': '7.0', 'prefecture': '東京都',
        })
        self.assertTrue(form.is_valid())

    def test_year_is_required(self):
        form = EarthquakeSearchForm(data={
            'min_magnitude': '3.0', 'max_magnitude': '7.0', 'prefecture': '東京都',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('year', form.errors)

    def test_prefecture_is_optional(self):
        form = EarthquakeSearchForm(data={
            'year': '2020', 'min_magnitude': '3.0', 'max_magnitude': '7.0',
        })
        self.assertTrue(form.is_valid())

    def test_unknown_prefecture_choice_is_rejected(self):
        form = EarthquakeSearchForm(data={
            'year': '2020', 'min_magnitude': '3.0', 'max_magnitude': '7.0', 'prefecture': '架空県',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('prefecture', form.errors)


class SafeConversionHelpersTest(TestCase):
    def test_safe_int_parses_valid_value(self):
        self.assertEqual(safe_int('2020'), 2020)

    def test_safe_int_falls_back_to_default_on_invalid_value(self):
        self.assertEqual(safe_int('not-a-year', default=1900), 1900)
        self.assertEqual(safe_int(None, default=2000), 2000)

    def test_safe_float_parses_valid_value(self):
        self.assertEqual(safe_float('3.5'), 3.5)

    def test_safe_float_falls_back_to_default_on_invalid_value(self):
        self.assertEqual(safe_float('n/a', default=1.0), 1.0)
        self.assertEqual(safe_float(None, default=5.0), 5.0)

