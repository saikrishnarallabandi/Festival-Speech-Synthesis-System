/*************************************************************************/
/*                                                                       */
/*                Centre for Speech Technology Research                  */
/*                 (University of Edinburgh, UK) and                     */
/*                           Korin Richmond                              */
/*                         Copyright (c) 2002                            */
/*                         All Rights Reserved.                          */
/*                                                                       */
/*  Permission is hereby granted, free of charge, to use and distribute  */
/*  this software and its documentation without restriction, including   */
/*  without limitation the rights to use, copy, modify, merge, publish,  */
/*  distribute, sublicense, and/or sell copies of this work, and to      */
/*  permit persons to whom this work is furnished to do so, subject to   */
/*  the following conditions:                                            */
/*                                                                       */
/*   1. The code must retain the above copyright notice, this list of    */
/*      conditions and the following disclaimer.                         */
/*   2. Any modifications must be clearly marked as such.                */
/*   3. Original authors' names are not deleted.                         */
/*   4. The authors' names are not used to endorse or promote products   */
/*      derived from this software without specific prior written        */
/*      permission.                                                      */
/*                                                                       */
/*  THE UNIVERSITY OF EDINBURGH AND THE CONTRIBUTORS TO THIS WORK        */
/*  DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING      */
/*  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT   */
/*  SHALL THE UNIVERSITY OF EDINBURGH NOR THE CONTRIBUTORS BE LIABLE     */
/*  FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES    */
/*  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN   */
/*  AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,          */
/*  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF       */
/*  THIS SOFTWARE.                                                       */
/*                                                                       */
/*************************************************************************/
/*                                                                       */
/*                          Author: Korin Richmond                       */
/*                            Date: October 2002                         */
/* --------------------------------------------------------------------- */
/*                                                                       */
/* Implementation of a viterbi decoder type                              */
/*                                                                       */
/*                                                                       */
/*                                                                       */
/*************************************************************************/

#ifndef __VITERBIDECODER_H__
#define __VITERBIDECODER_H__

#include "Decoder.h"
#include "EST_viterbi.h"

//  class ViterbiDecoder : public Decoder, private EST_Viterbi_Decoder
//  {
//    ViterbiDecoder() : EST_Viterbi_Decoder(0,0,-1) { };
//    virtual void initialise();
//    virtual ~ViterbiDecoder() {};
//  };

class ViterbiDecoder : public EST_Viterbi_Decoder
{
public:
  ViterbiDecoder(uclist_f_t a, unpath_f_t b, int num_states)
    : EST_Viterbi_Decoder( a, b, num_states );

  bool getBestPathEndPoint( EST_VTPath *p );
}

#endif //__VITERBIDECODER_H__
