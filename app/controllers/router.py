from fastapi import APIRouter
from app.controllers.v1.rbac.user_controller import user_router
from app.controllers.v1.rbac.roles_controller import roles_router
from app.controllers.v1.masterdata.accountant_controller import accountant_router
from app.controllers.v1.masterdata.accountant_bank_controller import accountant_bank_router
from app.controllers.v1.masterdata.client_controller import client_router
from app.controllers.v1.masterdata.client_bank_controller import client_bank_router

from app.controllers.v1.masterdata.employee_controller import employee_router
from app.controllers.v1.masterdata.employee_status_controller import employee_status_router
from app.controllers.v1.masterdata.city import city_router
from app.controllers.v1.masterdata.country import country_router
from app.controllers.v1.masterdata.province import province_router
from app.controllers.v1.masterdata.states import states_router
from app.controllers.v1.masterdata.department_controller import department_router
from app.controllers.v1.masterdata.designation_controller import designation_router
from app.controllers.v1.masterdata.team_controller import team_router
from app.controllers.v1.masterdata.location_controller import location_router
from app.controllers.v1.masterdata.reimbursement_controller import reimbursement_router
from app.controllers.v1.masterdata.deduction_controller import deduction_router
from app.controllers.v1.masterdata.earning_controller import earning_router
from app.controllers.v1.masterdata.tax_year_controller import tax_year_router
from app.controllers.v1.masterdata.payroll_frequencies_controller import payroll_frequencies_router


API_V1_STR = "/v1"
router = APIRouter()


router.include_router(user_router, prefix=API_V1_STR+"/user",
                      tags=["User"])

router.include_router(roles_router, prefix=API_V1_STR+"/roles",
                      tags=["Roles"])

router.include_router(accountant_router, prefix=f'{API_V1_STR}/accountants',
                          tags=["Accountants"])

router.include_router(accountant_bank_router, prefix=f'{API_V1_STR}/accountant-bank',
                          tags=["Accountants Bank"])

router.include_router(client_router, prefix=f'{API_V1_STR}/clients',
                          tags=["Clients"])

router.include_router(client_bank_router, prefix=f'{API_V1_STR}/client-bank',
                          tags=["Clients Bank"])

router.include_router(employee_router, prefix=f'{API_V1_STR}/employees',
                          tags=["Employees"])

router.include_router(employee_status_router, prefix=f'{API_V1_STR}/employees-status',
                          tags=["Employees Status"])

router.include_router(city_router, prefix=API_V1_STR+"/city",
                      tags=["City"])

router.include_router(country_router, prefix=API_V1_STR+"/country",
                      tags=["Country"])

router.include_router(province_router, prefix=API_V1_STR+"/Province",
                      tags=["Provinces"])

router.include_router(states_router, prefix=API_V1_STR+"/states",
                      tags=["States"])

router.include_router(department_router, prefix=API_V1_STR+"/departments",
                      tags=["Departments"])

router.include_router(designation_router, prefix=API_V1_STR+"/designations",
                      tags=["Designation"])

router.include_router(team_router, prefix=API_V1_STR+"/teams",
                      tags=["Teams"])

router.include_router(location_router, prefix=API_V1_STR+"/locations",
                      tags=["Location"])


router.include_router(deduction_router, prefix=API_V1_STR+"/deductions",
                      tags=["Deduction"])


router.include_router(earning_router, prefix=API_V1_STR+"/earnings",
                      tags=["Earning"])

router.include_router(reimbursement_router, prefix=API_V1_STR+"/reimbursement",
                      tags=["Reimbursement"])


router.include_router(tax_year_router, prefix=API_V1_STR+"/tax-year",
                      tags=["Tax Year"])


router.include_router(payroll_frequencies_router, prefix=API_V1_STR+"/payroll-frequencies",
                      tags=["Payroll Frequencies"])