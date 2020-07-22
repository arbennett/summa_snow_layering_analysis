import xarray as xr
import numpy as np
from pysumma.plotting.utils import justify


def filter_vars(ds):
    ds['mLayerNrgFlux']     = ds['mLayerNrgFlux'].where(ds['mLayerNrgFlux']  -9999, other=np.nan)
    ds['mLayerDepth']       = ds['mLayerDepth'].where(ds['mLayerDepth'] != -9999, other=np.nan)
    ds['mLayerTemp']        = ds['mLayerTemp'].where(ds['mLayerTemp'] != -9999, other=np.nan)
    ds['mLayerVolFracWat']  = ds['mLayerVolFracWat'].where(ds['mLayerVolFracWat'] != -9999, other=np.nan)
    ds['iLayerConductiveFlux'] = ds['iLayerConductiveFlux'].where(ds['iLayerConductiveFlux'] != -9999, other=np.nan)
    ds['iLayerAdvectiveFlux']  = ds['iLayerAdvectiveFlux'].where(ds['iLayerAdvectiveFlux'] != -9999, other=np.nan)
    ds['iLayerHeight']      = ds['iLayerHeight'].where(ds['iLayerHeight'] != -9999, other=np.nan)
    mLayerConductiveFlux = (ds['iLayerConductiveFlux'].rolling(dim={'ifcToto': 2}, min_periods=1)
                            .sum().isel(ifcToto=slice(1, None)).rename({'ifcToto': 'midToto'}))
    mLayerAdvectiveFlux  = (ds['iLayerAdvectiveFlux'].rolling(dim={'ifcToto': 2}, min_periods=1)
                            .sum().isel(ifcToto=slice(1, None)).rename({'ifcToto': 'midToto'}))
    mLayerNetNrgFlux = mLayerConductiveFlux #+ mLayerAdvectiveFlux
    #mLayerNetNrgFlux = mLayerAdvectiveFlux
    ds['mLayerNetNrgFlux'] = -mLayerNetNrgFlux #- ds['mLayerNrgFlux']
    return ds


def aggregate_variables(ds, timeagg='D', timeagg_wide='D'):
    #nrg = (ds['mLayerNrgFlux']).resample({'time':     timeagg_wide}).mean(skipna=True)
    nrg = (ds['mLayerNetNrgFlux']).resample({'time':     timeagg_wide}).mean(skipna=True).compute()
    height_w = (ds['iLayerHeight']).resample({'time': timeagg_wide}).mean(skipna=True).compute()
    depth = (ds['mLayerDepth']).resample({'time':     timeagg_wide}).mean(skipna=True).compute()
    height = (ds['iLayerHeight']).resample({'time': timeagg}).mean(skipna=True).compute()
    temp = (ds['mLayerTemp']).resample({'time': timeagg}).mean(skipna=True).compute()
    wat  = (ds['mLayerVolFracWat']).resample({'time': timeagg}).mean(skipna=True).compute()
    #nrg_scaled = np.log1p(nrg * depth)
    nrg_scaled = nrg
    temp_deficit = 273.16 - temp
    rho_wat = 1000.
    rho_air = 1.225
    density = (wat * rho_wat) + (1-wat) * rho_air
    Cs = 2108.
    cold_content = Cs * density * temp_deficit
    return temp, wat, height, nrg_scaled, height_w


def filter_layer_var(var, depth):
    vmask = var != -9999
    dmask = depth != -9999
    depth.values = justify(depth.where(dmask).values)
    var.values = justify(var.where(vmask).values)
    lo_depth = depth.where(depth > 0)
    hi_depth = depth.where(depth < 0)
    var = var.where((depth < 0).values[:,:-1])
    return var


def scalarSnowDensity(test_ds):
    rho_s = test_ds['scalarSWE'] / (1000 * test_ds['scalarSnowDepth'])
    rho_s = rho_s.where(~np.isnan(rho_s), other=0.0)
    return rho_s


def scalarColdContent(test_ds):
    temp_deficit = 273.15 - test_ds['scalarSnowTemp']
    Cs = 2108.
    return Cs * test_ds['scalarSWE'] * temp_deficit


def scalarSnowTemp(test_ds):
    temp = filter_layer_var(test_ds['mLayerTemp'], test_ds['iLayerHeight'])
    depth = filter_layer_var(test_ds['mLayerDepth'], test_ds['iLayerHeight'])
    sat = ((depth * temp).sum(dim='midToto')/depth.sum(dim='midToto'))
    return sat


def scalarSnowNrg(test_ds):
    nrg = filter_layer_var(test_ds['mLayerNrgFlux'], test_ds['iLayerHeight'])
    depth = filter_layer_var(test_ds['mLayerDepth'], test_ds['iLayerHeight'])
    ssn = (depth * nrg).sum(dim='midToto')
    return ssn


def generate_snow_vars(test_ds):
    test_ds['scalarSnowDensity'] = scalarSnowDensity(test_ds)
    test_ds['scalarSnowTemp'] = scalarSnowTemp(test_ds)
    test_ds['scalarColdContent'] = scalarColdContent(test_ds)
    test_ds['scalarSnowNrg'] = scalarSnowNrg(test_ds)
    test_ds['snowSurfaceNrgFlux'] = (test_ds['nSnow'] > 0) * test_ds['iLayerNrgFlux'].isel(ifcToto=1, drop=True)
    return test_ds


def subset_and_aggregate_ds(ds):
    ds['time'] = ds['time'].dt.round('H')
    ds = generate_snow_vars(ds)
    ds = ds.isel(hru=0)
    scalar_vars = []
    for k, v in ds.variables.items():
        if not ('ifcToto' in v.dims or 'midToto' in v.dims or 'midSnow' in v.dims or 'ifcSnow' in v.dims):
            scalar_vars.append(k)
    if 'nSnow' in scalar_vars:
        scalar_vars.remove('nSnow')
    if 'nLayers' in scalar_vars:
        scalar_vars.remove('nLayers')
    return ds[scalar_vars].load()


def calc_water_year(da):
    return da.dt.year + (da.dt.month >= 10).astype(int)


def nse(sim, obs):
    num = np.sum((obs - sim) ** 2)
    den = np.sum((obs - np.mean(obs)) ** 2)
    return 1 - (num /den)


def kge(simulation_s, evaluation):
    sim_mean = np.mean(simulation_s, axis=0, dtype=np.float64)
    obs_mean = np.mean(evaluation, dtype=np.float64)
    r = np.sum((simulation_s - sim_mean) * (evaluation - obs_mean), axis=0, dtype=np.float64) / \
        np.sqrt(np.sum((simulation_s - sim_mean) ** 2, axis=0, dtype=np.float64) *
                np.sum((evaluation - obs_mean) ** 2, dtype=np.float64))
    alpha = np.std(simulation_s, axis=0) / np.std(evaluation, dtype=np.float64)
    beta = np.sum(simulation_s, axis=0, dtype=np.float64) / np.sum(evaluation, dtype=np.float64)
    kge_ = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    return kge_


def snow_disappearance_date(swe):
    try:
        date_of_peak = swe['time'].values[swe.argmax()]
        end_date = swe['time'].values[-1]
        sub_swe = swe.sel(time=slice(date_of_peak, end_date))
        has_no_swe = sub_swe == 0
        only_no_swe = np.argwhere(has_no_swe.values)
        return sub_swe['time'].values[only_no_swe[0][0]]
    except:
        return np.datetime64('NaT')


def sdd_diff(swe1, swe2):
    diff = snow_disappearance_date(swe1) - snow_disappearance_date(swe2)
    if isinstance(diff, np.timedelta64):
        return diff.astype('timedelta64[h]') / np.timedelta64(1, 'D')
    else:
        return np.datetime64('NaT')


def peak_swe(swe):
    return swe.max().values[()]


def ps_diff(swe1, swe2):
    return peak_swe(swe1) - peak_swe(swe2)


def mbe(sim, obs):
    return np.nanmean(obs - sim)
