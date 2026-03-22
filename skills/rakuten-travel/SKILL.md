---
name: rakuten-travel
description: Search and compare Japan hotels on Rakuten Travel with room availability, real pricing, and reviews via the Rakuten API.
compatibility: Requires curl, jq, and APPLICATION_ID (Rakuten API Key) environment variable.
metadata:
  category: travel
  region: jp
  tags: hotels, accommodation, booking, rakuten, japan
---

# Rakuten Travel

Query Japanese hotel information and room availability via Rakuten Travel API.

## Environment Variables

Requires `APPLICATION_ID` (Rakuten API Key) environment variable.

## Direct API Calls with curl

### Hotel Search (SimpleHotelSearch)

Search nearby hotels by coordinates:
```bash
curl -s "https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?applicationId=$APPLICATION_ID&latitude=35.6895&longitude=139.6917&searchRadius=1&datumType=1&hits=10&formatVersion=2" | jq '.hotels[] | .[0].hotelBasicInfo | {hotelName, hotelNo, address2, reviewAverage, hotelMinCharge}'
```

### Vacancy Search (VacantHotelSearch)

Search hotels with available rooms for specific dates:
```bash
curl -s "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426?applicationId=$APPLICATION_ID&checkinDate=YYYY-MM-DD&checkoutDate=YYYY-MM-DD&adultNum=2&latitude=35.6895&longitude=139.6917&searchRadius=3&datumType=1&hits=10&formatVersion=2" | jq '.hotels[] | .[0].hotelBasicInfo | {hotelName, hotelMinCharge, reviewAverage}'
```

### ⚠️ Getting Real Prices (Important!)

`hotelMinCharge` is a "minimum reference price", **not the actual bookable price**! It can differ by 4-7x.

To get real prices, add `responseType=large` and extract from `.[3].roomInfo[1].dailyCharge.total`:

```bash
curl -s "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426?applicationId=$APPLICATION_ID&checkinDate=YYYY-MM-DD&checkoutDate=YYYY-MM-DD&adultNum=2&latitude=40.8246&longitude=140.7406&searchRadius=2&datumType=1&hits=5&formatVersion=2&responseType=large" | jq '[.hotels[] | {
  name: .[0].hotelBasicInfo.hotelName,
  rating: .[0].hotelBasicInfo.reviewAverage,
  price: .[3].roomInfo[1].dailyCharge.total
}] | sort_by(.price)'
```

**Response structure (responseType=large)**:
- `.[0]` - hotelBasicInfo (basic hotel info)
- `.[1]` - hotelDetailInfo (detailed info)
- `.[2]` - hotelReserveInfo (reservation info)
- `.[3]` - roomInfo (room info, contains real prices)
  - `.[3].roomInfo[0].roomBasicInfo` - room/plan details
  - `.[3].roomInfo[1].dailyCharge.total` - **real price (total for 2 guests)**

## Common Parameters

### Location (choose one)
- `latitude` + `longitude` + `searchRadius` + `datumType=1` - search by coordinates
- `hotelNo` - search by hotel number (multiple allowed, comma-separated)
- `largeClassCode=japan` + `middleClassCode` + `smallClassCode` - search by region code

### Required for Vacancy Search
- `checkinDate` - check-in date (YYYY-MM-DD)
- `checkoutDate` - check-out date (YYYY-MM-DD)
- `adultNum` - number of adults (1-4)

### Optional Parameters
- `hits` - number of results (1-30, default 30)
- `page` - page number
- `minCharge` / `maxCharge` - price range
- `searchRadius` - search radius in km (1-3)

## Common Region Codes

| Region | middleClassCode | smallClassCode examples |
|------|-----------------|---------------------|
| Tokyo | tokyo | shinjuku, shibuya, ginza |
| Osaka | osaka | umeda, namba, tennoji |
| Kyoto | kyoto | kawaramachi, gion |
| Hokkaido | hokkaido | sapporo, otaru |
| Okinawa | okinawa | naha |

## Response Fields

- `hotelName` - hotel name
- `hotelNo` - hotel number (for subsequent queries)
- `address1` + `address2` - address
- `reviewAverage` - rating (1-5)
- `reviewCount` - number of reviews
- `hotelMinCharge` - minimum price (JPY)
- `nearestStation` - nearest train station
- `access` - transportation info
- `hotelInformationUrl` - detail page link
