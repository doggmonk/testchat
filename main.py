import linecache
import re
import sys

from hamcrest import assert_that, is_, equal_to, not_, string_contains_in_order
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def get_exception_data():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    line_no = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, line_no, f.f_globals)
    return 'EXCEPTION ({}) IN ({}, LINE {} "{}"): {}'.format(exc_type, filename, line_no, line.strip(), exc_obj)


def wait_for_element(_driver, object_type, _object, element_wait=200):
    if object_type == 'css':
        object_type_obj = By.CSS_SELECTOR
    elif object_type == 'class':
        object_type_obj = By.CLASS_NAME
    elif object_type == 'id':
        object_type_obj = By.ID
    elif object_type == 'xpath':
        object_type_obj = By.XPATH
    else:
        raise NotImplementedError()

    try:
        WebDriverWait(_driver, element_wait).until(EC.presence_of_element_located((object_type_obj, _object)),
                                                   message='object type "{:s}" was not found by code "{:s}"'.format(
                                                   str(object_type_obj), str(_object)))
    except Exception as e:
        print('Exception=' + str(e))
        return False
    else:
        return True


def send_req(_driver, _conf, sql_request):
    _driver.get(_conf['link'])
    _driver.maximize_window()
    assert_that(_driver.title), is_(equal_to("SQL Tryit Editor"))
    wait_for_element(_driver, 'css', _conf['css']['sql_btn'])
    input_item = _driver.find_element_by_css_selector("div[class='CodeMirror cm-s-default CodeMirror-wrap']")
    _driver.execute_script("arguments[0].CodeMirror.setValue(\"" + _conf.get('sql_req').get(sql_request) + "\");",
                           input_item)
    button = _driver.find_element_by_css_selector(_conf['css']['sql_btn'])
    button.click()


def get_table_caption(_driver, _conf):
    table_rows = _driver.find_elements_by_css_selector(_conf['css']['table_row'])
    return table_rows[0]


def get_table_rows(_driver, _conf):
    table_rows = _driver.find_elements_by_css_selector(_conf['css']['table_row'])
    table_rows.pop(0)
    return table_rows


def get_column_id_by_name(column_name, _driver, _conf):
    caption_row = get_table_caption(_driver, _conf)
    for _id, item in enumerate(caption_row.find_elements_by_css_selector('th')):
        if column_name == item.get_attribute('innerHTML').strip():
            return _id

    return False


def get_row_columns_by_column_value(column_name, value, _driver, _conf):
    column_id = get_column_id_by_name(column_name, _driver, _conf)
    for item in get_table_rows(_driver, _conf):
        cells = item.find_elements_by_css_selector('td')
        page_value = cells[column_id].get_attribute('innerHTML').strip()
        if value == page_value:
            return cells
    return False


def all_column_value_count(column_name, value, _driver, _conf):
    column_id = get_column_id_by_name(column_name, _driver, _conf)
    if column_id is None:
        err = f'Column {column_name} not found.'
        raise ValueError(err)
    rows_found = 0
    for item in get_table_rows(_driver, _conf):
        columns = item.find_elements_by_css_selector('td')
        page_value = columns[column_id].get_attribute('innerHTML').strip()
        if value != page_value:
            err = f'Waiting for value {value}, but {page_value} found.'
            raise ValueError(err)
        else:
            rows_found += 1
    return rows_found


def result_count(_driver, _conf):
    return int(
        re.sub(r'Number of Records: ', '', _driver.find_element_by_css_selector(_conf['css']['res_number']).text))


def test_correct_contact_name_address(driver, conf_data):
    send_req(driver, conf_data, 'select_all')
    wait_for_element(driver, 'css', conf_data['css']['res_number'])
    cells = get_row_columns_by_column_value('ContactName', 'Giovanni Rovelli', driver, conf_data)
    addres_id = get_column_id_by_name('Address', driver, conf_data)
    page_address = cells[addres_id].get_attribute('innerHTML').strip()
    assert_that(page_address, is_('Via Ludovico il Moro 22'))


def test_all_customers_from_london(driver, conf_data):
    send_req(driver, conf_data, 'select_london')
    wait_for_element(driver, 'css', conf_data['css']['res_number'])
    rows_count = all_column_value_count('City', 'London', driver, conf_data)
    page_rows_count = result_count(driver, conf_data)
    assert_that(rows_count, is_(equal_to(page_rows_count)))


def test_insert_new_customer(driver, conf_data):
    send_req(driver, conf_data, 'check_new')
    wait_for_element(driver, 'css', conf_data['css']['made_changes'])
    assert_that("No result.", is_(driver.find_element_by_css_selector(conf_data['css']['made_changes']).text))
    send_req(driver, conf_data, 'insert_new')
    wait_for_element(driver, 'css', conf_data['css']['made_changes'])
    assert_that("You have made changes to the database. Rows affected: 1", is_(driver.find_element_by_css_selector(
                conf_data['css']['made_changes']).text))
    send_req(driver, conf_data, 'check_new')
    assert_that(result_count(driver, conf_data), is_(equal_to(1)))


def test_update_all_data_for_customer(driver, conf_data):
    send_req(driver, conf_data, 'check_new')
    wait_for_element(driver, 'css', conf_data['css']['res_number'])
    assert_that(result_count(driver, conf_data), is_(equal_to(1)))
    cell_old = get_row_columns_by_column_value('CustomerID', '99', driver, conf_data)
    send_req(driver, conf_data, 'update_new')
    wait_for_element(driver, 'css', conf_data['css']['made_changes'])
    assert_that("You have made changes to the database. Rows affected: 1", is_(driver.find_element_by_css_selector(
                conf_data['css']['made_changes']).text))
    send_req(driver, conf_data, 'check_new')
    cell_new = get_row_columns_by_column_value('CustomerID', '99', driver, conf_data)
    assert_that(cell_old, is_(not_(cell_new)))
    assert_that(result_count(driver, conf_data), is_(equal_to(1)))


def test_clean_base_after(driver, conf_data):
    wait_for_element(driver, 'css', conf_data['css']['restore_btn'])
    driver.find_element_by_css_selector(conf_data['css']['restore_btn']).click()
    alert_accept = driver.switch_to.alert
    assert_that(alert_accept.text, string_contains_in_order("action will restore the database"))
    alert_accept.accept()
    wait_for_element(driver, 'css', conf_data['css']['made_changes'])
    assert_that("The database is fully restored.", is_(driver.find_element_by_css_selector(
                conf_data['css']['made_changes']).text))
