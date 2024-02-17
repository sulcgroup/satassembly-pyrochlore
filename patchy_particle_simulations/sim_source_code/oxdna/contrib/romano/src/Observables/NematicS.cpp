/*
 * NematicS.cpp
 *
 *  Created on: Mar 10, 2016
 *      Author: flavio
 */

#include "NematicS.h"
#include <vector>

template<typename number> NematicS<number>::NematicS() {
    _axis_i = -1;
    _cluster_n_cutoff = 5;
    _cluster_angle_cutoff = 0.1;
    _cluster_distance_cutoff = 2.;
    _rod_length = 10.;
    _cells = NULL;
    _particles = NULL;
}

template<typename number>
NematicS<number>::~NematicS() {
    if (_particles != NULL) delete _particles;
}

template<typename number>
void NematicS<number>::init(ConfigInfo<number> &config_info) {
    BaseObservable<number>::init(config_info);

    int N = *config_info.N;

    _particles = new BaseParticle<number> * [N];
    for(int i = 0; i < N; i++)
        _particles[i] = config_info.particles[i];

    number rcut = _rod_length + _cluster_distance_cutoff;

    _cells = new Cells<number>(*config_info.N, config_info.box);
    _cells->init(_particles, rcut);

}

template<typename number>
void NematicS<number>::get_settings(input_file &my_inp, input_file &sim_inp) {
	std::string tmps;

    int tmpi;
	getInputInt(&my_inp, "ref_vec", &tmpi, 1);

	if (tmpi < 0 || tmpi >=6) throw oxDNAException ("Wrond index in observable nematic_s");
	_axis_i = tmpi;
	OX_LOG (Logger::LOG_INFO, "Using axis %d", _axis_i);
}

template<typename number>
LR_vector<number> * NematicS<number>::_get_axis(BaseParticle<number> * p) {
	switch (_axis_i) {
		case NematicS::O_V1: return &(p->orientation.v1);
		case NematicS::O_V2: return &(p->orientation.v2);
		case NematicS::O_V3: return &(p->orientation.v3);
		case NematicS::OT_V1: return &(p->orientationT.v1);
		case NematicS::OT_V2: return &(p->orientationT.v2);
		case NematicS::OT_V3: return &(p->orientationT.v3);
		default: throw oxDNAException ("Should never get here....");
	}
	return (LR_vector<number> *) NULL;
}

template<typename number>
std::vector<list<int> > NematicS<number>::build_clusters() {
    int N = *(this->_config_info.N);
    //BaseParticle<number> ** particles = this->_config_info.particles;

    _cells->global_update();

    std::vector<ParticlePair<number> > pairs = _cells->get_potential_interactions();

    std::vector<std::pair<int, int> > contacts;
    for (auto it = pairs.begin(); it != pairs.end(); it ++) {
        BaseParticle<number> * p = (*it).first;
        BaseParticle<number> * q = (*it).second;

        LR_vector<number> r = this->_config_info.box->min_image(p->pos, q->pos);

        number dist = InteractionUtils::spherocylinder_distance(r, p->orientation.v3, q->orientation.v3, _rod_length);
        if (dist < _cluster_distance_cutoff) {
            number dot = p->orientation.v3 * q->orientation.v3;
            if (dot < (number) 0.f)
                dot = -dot;
            if (acos(dot) < _cluster_angle_cutoff)
                contacts.push_back(std::pair<int,int>(p->index, q->index));
        }
    }


    // for each particle, we go through its neighbours and identify
    // who is closer to whom

    // try the spherocylinder overlap
/*    std::vector<std::pair<int, int> > contacts;
    for (int i = 0; i < N; i ++) {
        BaseParticle<number> *p = particles[i];
        for (int j = 0; j < i; j ++) {
            BaseParticle<number> *q = particles[j];
            LR_vector<number> r = this->_config_info.box->min_image(p->pos, q->pos);
            number dist = InteractionUtils::spherocylinder_distance(r, p->orientation.v3, q->orientation.v3, _rod_length);
            if (dist < 3.) {
                number dot = p->orientation.v3 * q->orientation.v3;
                if (dot < (number) 0.f)
                    dot = -dot;
                if (acos(dot) < _cluster_angle_cutoff)
                    contacts.push_back(std::pair<int,int>(i, j));
            }
        }
    }*/

    // now we have the contact list; we just need to set up the clusters

    std::vector<list<int> > clusters;
    std::vector<int> which_list;
    for (int i = 0; i < N; i ++) {
        list<int> mylist;
        mylist.push_back(i);
        clusters.push_back(mylist);
        which_list.push_back(i);
    }

    //printf ("this is how many contacts I found: %d\n", (int)contacts.size());
    for (auto it = contacts.begin(); it != contacts.end(); it++) {
        int i = (*it).first;
        int j = (*it).second;

        auto check = std::find(clusters[which_list[i]].begin(),
                                clusters[which_list[i]].end(), i);
        if (check == clusters[which_list[i]].end()) throw oxDNAException("WRING WRONG");
        check = std::find(clusters[which_list[j]].begin(),
                                clusters[which_list[j]].end(), j);
        if (check == clusters[which_list[j]].end()) throw oxDNAException("WRING WRANG");

        if (which_list[i] != which_list[j] or true) {
            std::list<int> * clustj = &(clusters[which_list[j]]);
            for (auto jt = clustj->begin(); jt != clustj->end(); jt++) {
                which_list[*jt] = which_list[i];
            }
            clusters[which_list[i]].merge(*clustj);
            clusters[which_list[i]].sort();
        }
    }

    // now we have a list of clusters, they can either be empty or full
    int check = 0;
    for (auto it = clusters.begin(); it != clusters.end(); it++) {
        check += it->size();
    }
    if (check != N) throw oxDNAException("WRONG WRONG WRONG...");
    return clusters;
}

template<typename number>
std::string NematicS<number>::get_output_string(llint curr_step) {
    int N = *(this->_config_info.N);
	BaseParticle<number> ** particles = this->_config_info.particles;

    std::vector<list<int> > clustid = build_clusters();

    std::string ret ("");

    number overall = 0.;
    int n_clusters = 0;
    for (auto it = clustid.begin(); it != clustid.end(); ++it) {
        if (it->size() > _cluster_n_cutoff) {
            // define my own nematic vector
            LR_vector<number> ndir (0., 0., 0.);
            number sum = (number) 0.f;
            for (auto jt = (*it).begin(); jt != (*it).end(); ++jt) {
                ndir += particles[*jt]->orientation.v3;
            }
            ndir.normalize();
            for (auto jt = (*it).begin(); jt != (*it).end(); ++jt) {
                LR_vector<number> * v = _get_axis(particles[*jt]);
                number dot = ndir * (*v);
                if (fabs(dot) >= 1.f) dot = copysign(1.f - FLT_EPSILON, dot);
                ndir += particles[*jt]->orientation.v3;
                sum += 1.5*(dot*dot) - 0.5;
            }
            overall = overall + sum;
            n_clusters = n_clusters + 1;
        }
    }
    if (n_clusters > 0)
        ret += Utils::sformat(" %g %g %d", overall / (number)N, overall / (number)n_clusters / (number)N, n_clusters);
    else
        ret += Utils::sformat(" %g %g %d", 0., 0., n_clusters);

    return ret;

}

template class NematicS<float>;
template class NematicS<double>;
