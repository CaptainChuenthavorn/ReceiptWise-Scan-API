venv\Scripts\activate.bat
python main.py
http://localhost:5000/process_image

example image post method in postman
{
    "image_url": "https://media.discordapp.net/attachments/1101061546991423518/1155894895370834021/IMG_0793.JPG?width=393&height=613"
}

output should get
{
    "amount": " 315.00",
    "date": [],
    "recipient_account_number": "N/A",
    "recipient_name": "N/A",
    "reference": "N/A",
    "sender_account_number": "xxx-8xx-3528",
    "sender_name": "นาย วิชริศ าเชยชม "
}

https://media.discordapp.net/attachments/1101061546991423518/1156424926312538192/IMG_0779.JPG?ex=651cd523&is=651b83a3&hm=5f07582ea3c548d620bc7358856dcafaed77b5e0e0749987a5b66e5be92bb11a&=&width=352&height=550


https://media.discordapp.net/attachments/1101061546991423518/1156419628579434556/IMG_0761.JPG?ex=651cd034&is=651b7eb4&hm=400581cad5af5e40ec930e3119420f73d05c369a416eefbaecec2293252362a7&=&width=352&height=550



https://media.discordapp.net/attachments/1101061546991423518/1156422694057811968/IMG_0763.JPG?ex=651cd30f&is=651b818f&hm=27b232d7014036d17d14d8574e63d013380617d0721f7df594cf651752c504e0&=&width=315&height=550


{
    "amount": [
        "54.00"
    ],
    "bank_accounts": "cscb x",
    "date": [
        "2023-06-03T20:05:00+07:00"
    ],
    "memo": [
        ""
    ],
    "recipient_name": [
        [
            "น.ส. ณัฐวดี ติณภูมิ ",
            " xxx-xxx-1324"
        ]
    ],
    "reference_number": [
        "2023060361lkacnj8u0qdm9ha"
    ],
    "sender_account_number": [
        "xxx-xxx588-5"
    ],
    "sender_name": [
        "นาย",
        "กฤษฎา",
        "สารวิทย์"
    ]
}