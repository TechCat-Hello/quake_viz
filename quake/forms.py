from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# ---- 新しいユーザー登録フォーム（メールアドレス付き） ----
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

# ---- 地震検索フォーム（既存のまま） ----
PREFECTURE_CHOICES = [
    ('', '全て'),
    ('北海道', '北海道'), ('青森県', '青森県'), ('岩手県', '岩手県'),
    ('宮城県', '宮城県'), ('秋田県', '秋田県'), ('山形県', '山形県'),
    ('福島県', '福島県'), ('茨城県', '茨城県'), ('栃木県', '栃木県'),
    ('群馬県', '群馬県'), ('埼玉県', '埼玉県'), ('千葉県', '千葉県'),
    ('東京都', '東京都'), ('神奈川県', '神奈川県'), ('新潟県', '新潟県'),
    ('富山県', '富山県'), ('石川県', '石川県'), ('福井県', '福井県'),
    ('山梨県', '山梨県'), ('長野県', '長野県'), ('岐阜県', '岐阜県'),
    ('静岡県', '静岡県'), ('愛知県', '愛知県'), ('三重県', '三重県'),
    ('滋賀県', '滋賀県'), ('京都府', '京都府'), ('大阪府', '大阪府'),
    ('兵庫県', '兵庫県'), ('奈良県', '奈良県'), ('和歌山県', '和歌山県'),
    ('鳥取県', '鳥取県'), ('島根県', '島根県'), ('岡山県', '岡山県'),
    ('広島県', '広島県'), ('山口県', '山口県'), ('徳島県', '徳島県'),
    ('香川県', '香川県'), ('愛媛県', '愛媛県'), ('高知県', '高知県'),
    ('福岡県', '福岡県'), ('佐賀県', '佐賀県'), ('長崎県', '長崎県'),
    ('熊本県', '熊本県'), ('大分県', '大分県'), ('宮崎県', '宮崎県'),
    ('鹿児島県', '鹿児島県'), ('沖縄県', '沖縄県'),
]

class EarthquakeSearchForm(forms.Form):
    start_year = forms.IntegerField(label='開始年', min_value=1900, max_value=2100)
    end_year = forms.IntegerField(label='終了年', min_value=1900, max_value=2100)

    min_magnitude = forms.FloatField(
        label='最小マグニチュード',
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '0.0',
            'max': '10.0',
            'step': '0.1',
            'oninput': 'document.getElementById("min_mag_val").innerText = this.value;'
        }),
        initial=3.0
    )

    max_magnitude = forms.FloatField(
        label='最大マグニチュード',
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '0.0',
            'max': '10.0',
            'step': '0.1',
            'oninput': 'document.getElementById("max_mag_val").innerText = this.value;'
        }),
        initial=7.0
    )

    prefecture = forms.ChoiceField(
        choices=PREFECTURE_CHOICES,
        required=False,
        label='都道府県'
    )
