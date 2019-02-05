import requests, json, csv


rodgort_url = "https://rodgort.sobotics.org/api/metaquestions?status=status-completed&pageSize=100&page={}"

old_records = []
status_completed_csvfile = "StatusCompletedBurninateRequests.csv"
split_csvfile = "SplitTags.csv"
with open(status_completed_csvfile) as csvfile: 
    reader = csv.reader(csvfile)
    next(reader)
    for record in reader:
        old_records.append(int(record[0]))


req = requests.get(rodgort_url.format(1))
data = json.loads(req.text)
total_pages = data["totalPages"]

new_records = []
new_split_records = []
for page_no in range(2, total_pages+1):
    for record in data["data"]:
        tags_per_record = []
        synonyms_per_record = []
        if any(meta_request_tag["tagName"] == "burninate-request" for meta_request_tag in record["metaRequestTags"]):
            for main_tag in record["mainTags"]:
                if main_tag["trackingStatusName"] == "Tracked":
                    tags_per_record.append(main_tag["tagName"])
                    synonyms_per_record.append(main_tag["synonymOf"])
        if tags_per_record and record["id"] not in old_records:
            csv_record = [record["id"], "[{}]".format(", ".join(tags_per_record))]
            new_records.append(csv_record)
            split_csv_records = []
            for tag, syn in zip(tags_per_record, synonyms_per_record):
                split_csv_records.append(["https://meta.stackoverflow.com/q/{}".format(record["id"]), "[{}]".format(tag), syn if syn else ""])
            new_split_records.extend(split_csv_records)


    req = requests.get(rodgort_url.format(page_no))
    data = json.loads(req.text)

with open(status_completed_csvfile, "a") as csvfile: 
    writer = csv.writer(csvfile, quotechar='"')
    writer.writerows(new_records)

with open(split_csvfile, "a") as csvfile: 
    writer = csv.writer(csvfile, quotechar='"')
    writer.writerows(new_split_records)

