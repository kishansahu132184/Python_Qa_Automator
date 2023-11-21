
   # using left join keeping structure as a base
                # df3 = techSpecDictionary.merge(
                #         df, on='Datalayer', how='left')
                # # after extracted DL values are mapped to base, now checking for eg : lets say some extra var populating in extracted data layer now after mapping to the base nan will be coming so removed that for clean look
                # df3['key_value'] = df3['key_value'].replace(np.nan, '')
                # # now at this place creating another df to basically hide the datalayer coloumn and making evar/props and keyvalue visible so to map this table with network call.
                # uat = df3[['eVar/Prop', 'key_value']]
                # print(uat)
                # print(pd.DataFrame(dataValues))

