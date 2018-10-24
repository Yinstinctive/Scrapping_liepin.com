import requests
from bs4 import BeautifulSoup
from time import sleep
from csv import DictWriter


def get_job_urls():
	base_url = "https://www.liepin.com"

	#搜索数据分析岗 - 杭州
	#岗位地点url: &dqs=070020
	url = "https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&dqs=070020&key=%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90"
	next_page_url = ""
	job_dict_list = []
	page_num = 1

	#读取每一页的职位信息的url并存入job_list_urls
	while next_page_url != "javascript:;":
		#在更新下一页href的url的时候， &dqs=070020有可能会丢失，
		#导致页面显示没有找到符合的职位,更新page_buttons的时候会报错，
		#加上表示岗位地点的url,&dqs=即可
		try:
			response = requests.get(url).text
			soup = BeautifulSoup(response,"html.parser")
			page_buttons = soup.find(class_="pagerbar").find_all("a")
			print(f"Currently scrapping Page {page_num}......")
			print(url)
		except AttributeError:
			url = f"{base_url}{next_page_url}/&dqs=070020"
			sleep(1)
			response = requests.get(url).text
			soup = BeautifulSoup(response,"html.parser")
			page_buttons = soup.find(class_="pagerbar").find_all("a")
			print(f"Currently scrapping Page {page_num}......")
			print(url)

		for button in page_buttons:
			if button.get_text() == "下一页":
				next_page_url = button["href"]
				index = next_page_url.index("curPage=")
				next_page_url = next_page_url[0:index:]+f"curPage={page_num-1}&curPage={page_num}"
				break

		job_list = soup.find_all(class_="job-info")

		for job in job_list:
			title = job.find("h3")["title"][2::]
			url_part = job.find("a")["href"]
			if base_url in url_part:
				job_link = url_part
			else:
				job_link = f"{base_url}{url_part}"
			details = job.find(class_="condition clearfix")
			salary = details.find(class_="text-warning").get_text()
			area = details.find(class_="area").get_text()
			edu = details.find(class_="edu").get_text()
			exp = details.find("span").find_next_siblings()[2].get_text()
			job_dict_list.append({
				"职位名称":title,
				"链接":job_link,
				"薪资":salary,
				"地区":area,
				"学历要求":edu,
				"工作经验要求":exp})

		url = f"{base_url}{next_page_url}"
		page_num += 1
		#检索前50页
		if page_num == 49:
			break
		sleep(1)

	#将job_list_urls写入csv文件
	with open("job_list.csv","w",newline="",encoding='utf-8-sig') as file:
		headers = [key for key in job_dict_list[0].keys()]
		csv_writer = DictWriter(file, fieldnames=headers)
		csv_writer.writeheader()
		for job in job_dict_list: 
			csv_writer.writerow(job)


get_job_urls()



