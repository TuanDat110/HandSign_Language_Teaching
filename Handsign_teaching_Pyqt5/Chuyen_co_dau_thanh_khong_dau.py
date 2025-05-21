

def ma_hoa_telex(ki_tu):
    kitu_1 = ""
    kitu_2 = ""
    output = [];
    input = ki_tu
#   mã hóa chữ a
    if input == "á" :
        kitu_1 = "a"
        kitu_2 = "sac"
    elif input == "à" :
        kitu_1 = "a"
        kitu_2 = "huyen"
    elif input == "ả" :
        kitu_1 = "a"
        kitu_2 = "hoi"
    elif input == "ã" :
        kitu_1 = "a"
        kitu_2 = "nga"
    elif input == "ạ" :
        kitu_1 = "a"
        kitu_2 = "nang"
#   mã hóa chữ ă
    elif input == "ă" :
        kitu_1 = "aw"
    elif input == "ắ" :
        kitu_1 = "aw"
        kitu_2 = "sac"
    elif input == "ằ" :
        kitu_1 = "aw"
        kitu_2 = "huyen"
    elif input == "ẳ" :
        kitu_1 = "aw"
        kitu_2 = "hoi"
    elif input == "ẵ" :
        kitu_1 = "aw"
        kitu_2 = "nga"
    elif input == "ặ" :
        kitu_1 = "aw"
        kitu_2 = "nang"
#   mã hóa chữ â
    elif input == "â" :
        kitu_1 = "aa"
    elif input == "ấ" :
        kitu_1 = "aa"
        kitu_2 = "sac"
    elif input == "ầ" :
        kitu_1 = "aa"
        kitu_2 = "huyen"
    elif input == "ẩ" :
        kitu_1 = "aa"
        kitu_2 = "hoi"
    elif input == "ẫ" :
        kitu_1 = "aa"
        kitu_2 = "nga"
    elif input == "ậ" :
        kitu_1 = "aa"
        kitu_2 = "nang"
#   mã hóa chữ e
    elif input == "é" :
        kitu_1 = "e"
        kitu_2 = "sac"
    elif input == "è" :
        kitu_1 = "e"
        kitu_2 = "huyen"
    elif input == "ẻ" :
        kitu_1 = "e"
        kitu_2 = "hoi"
    elif input == "ẽ" :
        kitu_1 = "e"
        kitu_2 = "nga"
    elif input == "ẹ" :
        kitu_1 = "e"
        kitu_2 = "nang"
#   mã hóa chữ ê
    elif input == "ê" :
        kitu_1 = "ee"
    elif input == "ế" :
        kitu_1 = "ee"
        kitu_2 = "sac"
    elif input == "ề" :
        kitu_1 = "ee"
        kitu_2 = "huyen"
    elif input == "ể" :
        kitu_1 = "ee"
        kitu_2 = "hoi"
    elif input == "ễ" :
        kitu_1 = "ee"
        kitu_2 = "nga"
    elif input == "ệ" :
        kitu_1 = "ee"
        kitu_2 = "nang"
#   mã hóa chữ i
    elif input == "í" :
        kitu_1 = "i"
        kitu_2 = "sac"
    elif input == "ì" :
        kitu_1 = "i"
        kitu_2 = "huyen"
    elif input == "ỉ" :
        kitu_1 = "i"
        kitu_2 = "hoi"
    elif input == "ĩ" :
        kitu_1 = "i"
        kitu_2 = "nga"
    elif input == "ị" :
        kitu_1 = "i"
        kitu_2 = "nang"
#   mã hóa chữ o
    elif input == "ó" :
        kitu_1 = "o"
        kitu_2 = "sac"
    elif input == "ò" :
        kitu_1 = "o"
        kitu_2 = "huyen"
    elif input == "ỏ" :
        kitu_1 = "o"
        kitu_2 = "hoi"
    elif input == "õ" :
        kitu_1 = "o"
        kitu_2 = "nga"
    elif input == "ọ" :
        kitu_1 = "o"
        kitu_2 = "nang"
#   mã hóa chữ ô
    elif input == "ô" :
        kitu_1 = "oo"
    elif input == "ố" :
        kitu_1 = "oo"
        kitu_2 = "sac"
    elif input == "ồ" :
        kitu_1 = "oo"
        kitu_2 = "huyen"
    elif input == "ổ" :
        kitu_1 = "oo"
        kitu_2 = "hoi"
    elif input == "ỗ" :
        kitu_1 = "oo"
        kitu_2 = "nga"
    elif input == "ộ" :
        kitu_1 = "oo"
        kitu_2 = "nang"
#   mã hóa chữ ơ
    elif input == "ơ" :
        kitu_1 = "ow"
    elif input == "ớ" :
        kitu_1 = "ow"
        kitu_2 = "sac"
    elif input == "ờ" :
        kitu_1 = "ow"
        kitu_2 = "huyen"
    elif input == "ở" :
        kitu_1 = "ow"
        kitu_2 = "hoi"
    elif input == "ỡ" :
        kitu_1 = "ow"
        kitu_2 = "nga"
    elif input == "ợ" :
        kitu_1 = "ow"
        kitu_2 = "nang"
#   mã hóa chữ u
    elif input == "ú" :
        kitu_1 = "u"
        kitu_2 = "sac"
    elif input == "ù" :
        kitu_1 = "u"
        kitu_2 = "huyen"
    elif input == "ủ" :
        kitu_1 = "u"
        kitu_2 = "hoi"
    elif input == "ũ" :
        kitu_1 = "u"
        kitu_2 = "nga"
    elif input == "ụ" :
        kitu_1 = "u"
        kitu_2 = "nang"
#   mã hóa chữ ư
    elif input == "ư" :
        kitu_1 = "uw"
    elif input == "ứ" :
        kitu_1 = "uw"
        kitu_2 = "sac"
    elif input == "ừ" :
        kitu_1 = "uw"
        kitu_2 = "huyen"
    elif input == "ử" :
        kitu_1 = "uw"
        kitu_2 = "hoi"
    elif input == "ữ" :
        kitu_1 = "uw"
        kitu_2 = "nga"
    elif input == "ự" :
        kitu_1 = "uw"
        kitu_2 = "nang"
#   mã hóa chữ D
    elif input == "đ" :
        kitu_1 = "dd"

    elif input == " " :
        kitu_1 = "space"
    else:
        kitu_1 = input
    output.append(kitu_1)
    output.append(kitu_2)
    return output

# print(len(s))
# for char in s:
#     kt_ss = ma_hoa_telex(char)
#     print (kt_ss)
