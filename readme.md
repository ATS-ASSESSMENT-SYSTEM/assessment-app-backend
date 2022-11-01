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
        - information
        - timestamp (date_created and date_updated)
        - creater (FK => user)

    - View (Task)
        - create, edit and delete
        - List all categories and number of questions available in each category
        - get a category (View question from category)


### Question (Developer: Yusuff Adekunle )
    - Model (Task)
        - category (FK => category )
        - question_text
        - timestamp (date_created and date_updated)
        - creater (FK => user)
        - types (Practice, Real)
        - difficulty (easy, intermidiate, experienced )
    
    - Views (Task)
        - create, edit and delete
        - get a question with choices
        - filter question by type
        - filter question by difficulty

### Chioces  (Developer: Yusuff Adekunle )
    - Model (Task)
        - Question (FK)
        - choice_text
        - is_correct
        - timestamp

### Result (Developer: Tolu Smith )
    - Models (Task)
        - assessment (FK => assessment)
        - candidate (FK => User )
        - test_category (M2M)
        - timestamps
        - is_active
    
    - Views (Task)
        - create an instance of result
        - calculate total and send to application server
        - get result for a candidate
        - taking the assessment 


### System Logs (Developer: Tolu Smith)
    - Model (Task)
        - level
        - timestamp
        - event
        - message
    - Functions (Task)
