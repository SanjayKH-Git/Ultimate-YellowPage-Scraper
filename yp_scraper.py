import streamlit as st
import time
import csv
import googlesearch
import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as Bs
from lxml import etree
from tqdm import tqdm
import json
import os
import re
import pandas as pd
import sqlite3
import math


def yp_au_scrape(clue="", loc_clue="", direct_url=""):
    All_result_dict = {}
    try:
        # clue = "chirofactor"
        # loc_clue = "Brisbane"
        output_file = "Output_Files/yp_au.csv"

        if direct_url:
            main_url = direct_url
        else:
            main_url = f"https://www.yellowpages.com.au/search/listings?clue={clue}&locationClue={loc_clue.replace(' ', '%20')}"

        st.write(f"Searching URL: {main_url}")

        main_resp = requests.get(main_url, headers={"User-Agent": "Mozilla/5.0"})
        main_soup = Bs(main_resp.text, "html.parser")
        dom = etree.HTML(str(main_soup))
        main_resp.close()

        item_count = int(
            dom.xpath("//h2[contains(., 'Results for')]/text()")[0].split()[0]
        )
        cnt = 0
        max_page = math.ceil(item_count / 35)
        if max_page < 2:
            max_page = 2
            st.write(f"Total {max_page - 1} Page")
        else:
            st.write(f"Total {max_page} Pages")

        print(max_page)
        progress_bar = st.progress(0)
        for page in range(1, max_page + 1):
            main_resp = requests.get(
                f"{main_url}&pageNumber={page}", headers={"User-Agent": "Mozilla/5.0"}
            )
            print(f"{main_url}&pageNumber={page}")

            main_soup = Bs(main_resp.text, "html.parser")
            dom = etree.HTML(str(main_soup))
            main_resp.close()

            card_list = main_soup.find_all("div", class_="Box__Div-sc-dws99b-0 dAyAhR")
            print(len(card_list))
            for card in card_list:
                try:
                    card_dom = etree.HTML(str(card.parent()))
                    title = "".join(
                        card_dom.xpath(
                            "//a[@class='MuiTypography-root MuiLink-root MuiLink-underlineNone MuiTypography-colorPrimary']//h3/text()"
                        )[:1]
                    )

                    phone_No = "".join(
                        card_dom.xpath(
                            "//button[@class='MuiButtonBase-root MuiButton-root MuiButton-text ButtonPhone MuiButton-textPrimary MuiButton-fullWidth']//span/text()"
                        )[:1]
                    )
                    website = "".join(card_dom.xpath("//a[.='View Website']/@href")[:1])
                    yp_url = "https://www.yellowpages.com.au" + "".join(
                        card_dom.xpath(
                            "//a[@class='MuiTypography-root MuiLink-root MuiLink-underlineNone MuiTypography-colorPrimary']/@href"
                        )[:1]
                    )
                    yp_resp = requests.get(
                        yp_url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    yp_soup = Bs(yp_resp.text, "html.parser")
                    yp_dom = etree.HTML(str(yp_soup))
                    yp_resp.close()

                    email = "".join(
                        yp_dom.xpath(
                            "//a[@class='contact contact-main contact-email']/@data-email"
                        )
                    )
                    if not email:
                        Google_Search_url = (
                            f"https://www.google.com/search?q={title}+email+address"
                        )
                        search_resp = requests.get(
                            Google_Search_url, headers={"User-Agent": "Mozilla/5.0"}
                        )
                        email_pattern = (
                            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,4}"
                        )
                        email = ", ".join(re.findall(email_pattern, search_resp.text))

                    address = "".join(
                        yp_dom.xpath(
                            "//div[@class='listing-address mappable-address mappable-address-with-poi']/text()"
                        )
                    )

                    result_dict = {
                        "YP URL": yp_url,
                        "Business Name": title,
                        "Website URL": website,
                        "phone_No Number": phone_No,
                        "Physical Address": address,
                        "Email": email,
                    }
                    All_result_dict[result_dict["Business Name"]] = result_dict

                    headers = result_dict.keys()

                    df = pd.DataFrame([result_dict.values()], columns=headers)

                    if cnt == 0:
                        st_df = st.dataframe(df)
                    else:
                        st_df.add_rows(df)

                    cnt += 1
                except Exception as e:
                    print(e)

            progress_bar.progress((page / (max_page - 1)))

    except Exception as e:
        print(e)

    return All_result_dict


def yp_us_scrape(clue="", loc_clue="", direct_url=""):
    try:
        print("canada")
        All_result_dict = {}
        output_file = "Output_Files/yp_us.csv"

        if direct_url:
            main_url = direct_url
        else:
            main_url = f"https://www.yellowpages.com/search?search_terms={clue}&geo_location_terms={loc_clue}"

        st.write(f"Searching URL: {main_url}")

        main_resp = requests.get(main_url, headers={"User-Agent": "Mozilla/5.0"})
        main_soup = Bs(main_resp.text, "html.parser")
        dom = etree.HTML(str(main_soup))
        main_resp.close()

        item_count_text = "".join(
            dom.xpath("//span[@class='showing-count']/text()")
        ).split()[-1]
        item_count = int(item_count_text)
        cnt = 0
        max_page = math.ceil(item_count / 30)

        print(max_page)
        st.write(f"Total {max_page} Pages")
        progress_bar = st.progress(0)
        for page in range(1, max_page):
            main_url = main_url.split("&page")[0] + f"&page={page}"
            print(main_url)
            main_resp = requests.get(main_url, headers={"User-Agent": "Mozilla/5.0"})
            main_soup = Bs(main_resp.text, "html.parser")
            dom = etree.HTML(str(main_soup))
            main_resp.close()

            us_card_list = [
                (
                    "".join(a.xpath(".//text()")),
                    "https://www.yellowpages.com" + a.get("href"),
                )
                for a in dom.xpath(
                    "//div[@class='info-section info-primary']//a[@class='business-name']"
                )
            ]
            print(len(us_card_list))

            for title, yp_url in us_card_list:
                # count += 1
                biz_resp = requests.get(yp_url, headers={"User-Agent": "Mozilla/5.0"})
                biz_soup = Bs(biz_resp.text, "html.parser")
                biz_dom = etree.HTML(str(biz_soup))
                biz_resp.close()

                json_script = json.loads(
                    biz_soup.find("script", type="application/ld+json").text
                )

                # print(json_script)

                try:
                    website = json_script["url"]
                except Exception:
                    website = ""

                try:
                    phone_No = json_script["telephone"]
                except Exception:
                    phone_No = ""

                try:
                    email = json_script["email"].replace("mailto:", "")
                except Exception:
                    email = ""

                try:
                    address = "".join(
                        biz_dom.xpath("//span[contains(., 'Address:')]/../text()")
                    )
                except Exception:
                    address = ""

                result_dict = {
                    "YP URL": yp_url,
                    "Business Name": title,
                    "Website URL": website,
                    "Phone Number": phone_No,
                    "Physical Address": address,
                    "Email": email,
                }
                All_result_dict[result_dict["Business Name"]] = result_dict

                headers = result_dict.keys()

                df = pd.DataFrame([result_dict.values()], columns=headers)

                if cnt == 0:
                    st_df = st.dataframe(df)
                else:
                    st_df.add_rows(df)

                cnt += 1

                progress_bar.progress((page / (max_page - 1)))

    except Exception as e:
        print(e)

    return All_result_dict


def yp_ca_scrape(clue="", loc_clue="", direct_url=""):
    try:
        All_result_dict = {}
        output_file = "Output_Files/yp_ca.csv"

        if direct_url:
            main_url = direct_url
        else:
            main_url = f"https://www.yellowpages.ca/search/si/1/{clue}/{loc_clue.replace(' ', '+')}"

        st.write(f"Searching URL: {main_url}")

        main_resp = requests.get(main_url, headers={"User-Agent": "Mozilla/5.0"})
        main_soup = Bs(main_resp.text, "html.parser")
        dom = etree.HTML(str(main_soup))
        main_resp.close()

        max_page = int(
            "".join(dom.xpath("//span[@class='pageCount']//span/text()"))[-1]
        )

        cnt = 0

        print(max_page)
        st.write(f"Total {max_page} Pages")

        progress_bar = st.progress(0)

        for page in range(1, max_page + 1):
            main_url = main_url.replace("si/1", f"si/{page}")
            print(main_url)
            main_resp = requests.get(main_url, headers={"User-Agent": "Mozilla/5.0"})
            main_soup = Bs(main_resp.text, "html.parser")
            dom = etree.HTML(str(main_soup))
            main_resp.close()

            ca_card_list = dom.xpath("//div[@class='listing__content__wrapper']")

            # for title, yp_url in ca_card_list:
            for div in ca_card_list:
                yp_a = div.xpath(
                    ".//a[@class='listing__name--link listing__link jsListingName']"
                )[0]
                yp_url = "https://www.yellowpages.ca" + yp_a.get("href")
                title = "".join(yp_a.xpath("./text()"))
                website = "https://www.yellowpages.ca" + "".join(
                    div.xpath(".//a[@class='mlr__item__cta']/@href")
                )
                phone_No = "".join(
                    div.xpath(".//li[@class='mlr__submenu__item']/h4/text()")
                )
                address = " ".join(
                    div.xpath(".//span[@class='listing__address--full']//span/text()")
                )

                Google_Search_url = (
                    f"https://www.google.com/search?q={title}+email+address"
                )
                search_resp = requests.get(
                    Google_Search_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,4}"
                email_list = list(set(re.findall(email_pattern, search_resp.text)))
                if not email_list:
                    email_list = [
                        "",
                    ]

                result_dict = {
                    "YP URL": yp_url,
                    "Business Name": title,
                    "Website URL": website,
                    "Phone Number": phone_No,
                    "Physical Address": address,
                    "Email": email_list,
                }
                All_result_dict[result_dict["Business Name"]] = result_dict

                headers = result_dict.keys()

                df = pd.DataFrame([result_dict.values()], columns=headers)

                if cnt == 0:
                    st_df = st.dataframe(df)
                else:
                    st_df.add_rows(df)

                cnt += 1

                progress_bar.progress((page / (max_page)))

    except Exception as e:
        print(e)

    return All_result_dict


def yp_nz_scrape(clue="", loc_clue="", direct_url=""):
    try:
        All_result_dict = {}
        output_file = "Output_Files/yp_ca.csv"

        if direct_url:
            main_url = direct_url
            if "page" not in direct_url:
                main_url = direct_url
            else:
                main_url = direct_url.split("page/")[0]

        else:
            main_url = f"https://yellow.co.nz/{loc_clue}/{clue}"

        st.write(f"Searching URL: {main_url}")

        # print(main_url)
        main_resp = requests.get(main_url, headers={"User-Agent": "Mozilla/5.0"})
        main_soup = Bs(main_resp.text, "html.parser")
        dom = etree.HTML(str(main_soup))
        main_resp.close()

        json_script = json.loads(main_soup.find("script", type="application/json").text)
        max_page = json_script["props"]["pageProps"]["initialState"]["srp"]["data"][
            "results"
        ]["pageCount"]
        print(max_page)
        st.write(f"Total {max_page} Pages")

        progress_bar = st.progress(0)
        cnt = 0
        for page in range(1, max_page):
            page_url = main_url + f"/page/{page}"
            print(page_url)
            main_resp = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"})
            main_soup = Bs(main_resp.text, "html.parser")
            dom = etree.HTML(str(main_soup))
            main_resp.close()

            nz_card_list = dom.xpath(
                "//div[@class='p-4 border border-solid border-gray-200 shadow w-full false']"
            )

            for div in nz_card_list:
                try:
                    try:
                        yp_a = div.xpath(".//a[@itemprop='name']")[0]
                        yp_url = "https://yellow.co.nz" + yp_a.get("href")
                        title = "".join(yp_a.xpath("./h1/text()"))
                    except Exception:
                        yp_url = ""
                        title = ""
                    try:
                        phone_web_list = div.xpath(".//meta/@content")
                        phone_No = phone_web_list[0]

                        if len(phone_web_list) > 1:
                            website = phone_web_list[1]
                        else:
                            query = f"{title} website"
                            # search_results = search(query)
                            try:
                                website = next(
                                    googlesearch.search(query, num=5, stop=2, pause=2)
                                )
                            except Exception:
                                website = ""

                    except Exception:
                        phone_No = ""
                        website = ""

                    try:
                        address = "".join(
                            div.xpath(".//span[@itemprop='streetAddress']/text()")
                        )
                    except Exception:
                        address = ""
                    try:
                        Google_Search_url = (
                            f"https://www.google.com/search?q={title}+email+address"
                        )
                        search_resp = requests.get(
                            Google_Search_url, headers={"User-Agent": "Mozilla/5.0"}
                        )
                        email_pattern = (
                            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,4}"
                        )
                        email_list = list(
                            set(re.findall(email_pattern, search_resp.text))
                        )
                        if not email_list:
                            email_list = [
                                "",
                            ]

                    except Exception:
                        email_list = [
                            "",
                        ]

                    result_dict = {
                        "YP URL": yp_url,
                        "Business Name": title,
                        "Website URL": website,
                        "Phone Number": phone_No,
                        "Physical Address": address,
                        "Email": email_list,
                    }
                    print(result_dict)

                    All_result_dict[result_dict["Business Name"]] = result_dict

                    headers = result_dict.keys()

                    df = pd.DataFrame([result_dict.values()], columns=headers)

                    if cnt == 0:
                        st_df = st.dataframe(df)
                    else:
                        st_df.add_rows(df)

                    cnt += 1

                    progress_bar.progress((page / (max_page - 1)))

                except Exception as e:
                    print(e)

    except Exception as e:
        print(e)

    return All_result_dict


# clue=""
# loc_clue=""
# direct_url = "https://yellow.co.nz/Wellington/Dentists/page/1?what=Dentists&where=Wellington"
# yp = yp_nz_scrape(clue, loc_clue, direct_url)
