## List of Apps
### Assessment (Developer: Faith Adeosun)
    - Models (Task)
      - name
      - creator (FK => user)
      - timestamps (date_created and date_updated)
      - application_type
    
    - Views (Task)
        - create, edit and delete
        - list all assessment
        - get an assessment
    

### Category (M2M => assessment) (Developer: Yusuff Adekunle )
    - Model (Task)
        - assessment (M2M => assessment)
        - name
        - timestamp (date_created and date_updated)
        - creater (FK => user)

    - View (Task)
        - create, edit and delete
        - List all categories and number of questions available in each category
        - get a category (View question from category)


### Question (Developer: Yusuff Adekunle )
    - Model
        -