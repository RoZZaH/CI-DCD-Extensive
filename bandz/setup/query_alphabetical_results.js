// Stages that have been excluded from the aggregation pipeline query
__3tsoftwarelabs_disabled_aggregation_stages = [

	{
		// Stage 2 - excluded
		stage: 2,  source: {
			$facet: {
			    "outputField1": [ {
			        $bucket: {
			            groupBy: { "$substr": ['$catalogue_name', 0, 1]},
			            boundaries: ['A','B','C'],
			            default: "Other",
			            output:  {"bands": { "$push": {"band name": "$band_name", "genres" : "$genres"}}}
			        } 
			    }  ],
			    "genres": [
			        {"$unwind": "$genres"},
			        {"$group": { "_id": "null", "genres": {"$addToSet": "$genres"} }},
			        {"$sort": {"genres": 1 }}
			         ],
			
			}
		}
	},
]

db.getCollection("band").aggregate(

	// Pipeline
	[
		// Stage 1
		{
			$match: {
			    // enter query here
			    'genres': {$in: ['blues', 'electronic', 'indie']},
			    'hometown.county' : {$in: ['Clare', 'Cork', 'Kerry', 'Limerick', 'Tipperary', 'Waterford']}
			}
		},

		// Stage 3
		{
			$group: {
			    _id: { "$substr": ['$catalogue_name', 0, 1]},
			    bands: {$push : "$$ROOT"}
			    
			}
		},

		// Stage 4
		{
			$project: {
			    _id: 0,
			    key: "$_id",
			    value: "$bands"
			}
		},

	]

	// Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

);

$match: {
	
			    'genres': {$in: ['blues', 'electronic', 'indie']},
			    'hometown.county' : {$in: ['Clare', 'Cork', 'Kerry', 'Limerick', 'Tipperary', 'Waterford']}
}

$facet: 
	{
    "numbers_by_letter": [ { $group: {
    // enter query here
    _id: {$substr: ["$catalogue_name",0,1]},
    bands: {$sum: 1}
}}
     ],
    "bands_by_letter": [
        { $match: {
			    // enter query here
			    "catalogue_name": { $regex: /^A/}
			}
        } 
        
 ],
    // add more facets
}
}